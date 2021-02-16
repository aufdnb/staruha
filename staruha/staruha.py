import json
from collections import namedtuple
from datetime import datetime, timedelta
from typing import List

import nltk
import pandas as pd
from boto3 import session
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud

nltk.download("punkt")
nltk.download("stopwords")
STOP_WORDS = stopwords.words("english")

Key = namedtuple("Key", ["path", "date"])
TIME_INTERVAL_HOURS = 15


def create_key(path):
    date = path.split("/")[-1]
    path = path
    return Key(path=path, date=datetime.strptime(date, "%Y-%m-%d-%H-%M-%S"))


class Staruha:
    def __init__(
        self,
        *,
        rupor,
        aws_access_key_id,
        aws_secret_access_key,
        bucket_name="default_bucket",
    ):
        self.session = session.Session()
        self.s3 = self.session.client(
            "s3",
            region_name="nyc1",
            endpoint_url="https://sfo2.digitaloceanspaces.com",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.rupor = rupor
        self.bucket_name = bucket_name

    def get_keys(self) -> List[str]:
        response = self.s3.list_objects_v2(
            Bucket="athena-monitoring-store", Prefix="krisa/wallstreetbets/posts/"
        )

        keys = []
        done = False
        while not done:
            posts = response["Contents"]
            for post in posts:
                keys.append(post["Key"])
            done = not response["IsTruncated"]
            if not done:
                response = self.s3.list_objects_v2(
                    Bucket="athena-monitoring-store",
                    Prefix="krisa/wallstreetbets/posts/",
                    ContinuationToken=response["NextContinuationToken"],
                )

        return keys

    def get_ticker_sets(self):
        def get_ticker_set(exchange_store):
            return {ticker.split(":")[1] for ticker in exchange_store}

        result = self.s3.get_object(
            Bucket="athena-monitoring-store", Key="ticker_data/nasdaq_data.json"
        )
        nasdaq_data = json.loads(result["Body"].read().decode())

        result = self.s3.get_object(
            Bucket="athena-monitoring-store", Key="ticker_data/nyse_data.json"
        )
        nyse_data = json.loads(result["Body"].read().decode())

        result = self.s3.get_object(
            Bucket="athena-monitoring-store", Key="ticker_data/toronto_data.json"
        )
        toronto_data = json.loads(result["Body"].read().decode())

        nyse_tickers = get_ticker_set(nyse_data)
        nasdaq_tickers = get_ticker_set(nasdaq_data)
        toronto_tickers = get_ticker_set(toronto_data)

        return nyse_tickers, nasdaq_tickers, toronto_tickers

    def load_keys(self, keys):
        all_rows = []

        for post in keys:
            result = self.s3.get_object(Bucket="athena-monitoring-store", Key=post)
            text = result["Body"].read().decode()

            if not text:
                print("post {0}".format(post))
                continue

            post_dump = json.loads(text)
            all_rows.append(post_dump)
        return all_rows

    def create_rows(self, all_rows):
        fields = [
            "title",
            "created_utc",
            "selftext",
            "author_premium",
            "author_fullname",
            "id",
        ]

        def create_row(raw_data):
            try:
                data = {field: raw_data[field] for field in fields}
            except KeyError:
                raise
            return data

        clean_rows = []
        for row in all_rows:
            if isinstance(row, list):
                for d in row:
                    clean_rows.append(create_row(d))
                continue
            clean_rows.append(create_row(row))

        return clean_rows

    def generate_word_cloud(self, df: pd.DataFrame):
        def flatten(nested_list):
            for element in nested_list:
                if isinstance(element, list):
                    for x in element:
                        yield x
                else:
                    yield element

        nyse_tickers, nasdaq_tickers, toronto_tickers = self.get_ticker_sets()
        titles = [t for t in df.title]
        clean_titles = [
            title
            for title in list(flatten(map(word_tokenize, titles)))
            if title not in STOP_WORDS
        ]

        processed_titles = [
            x
            for x in clean_titles
            if x in nyse_tickers or x in nasdaq_tickers or x in toronto_tickers
        ]
        text = " ".join(x for x in processed_titles)
        wordcloud = WordCloud().generate(text)
        wordcloud.to_file("word_cloud.png")
        return "word_cloud.png"

    def run(self):
        keys = self.get_keys()
        dated_keys = [create_key(key) for key in keys]

        keys_in_window = [
            key.path
            for key in filter(
                lambda x: datetime.utcnow() - timedelta(hours=TIME_INTERVAL_HOURS)
                <= x.date
                < datetime.utcnow(),
                dated_keys,
            )
        ]

        raw_data = self.load_keys(keys_in_window)
        clean_rows = self.create_rows(raw_data)
        df = pd.DataFrame(data=clean_rows)
        image_path = self.generate_word_cloud(df)

        self.rupor.send(
            image_path, f"Внучки, смотри что нашла для: {datetime.utcnow()} UTC period: {TIME_INTERVAL_HOURS}hrs"
        )
