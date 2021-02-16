import staruha
import sys
import click
import logging
from .rupor import SlackRupor
from .staruha import Staruha


@click.command()
@click.option("--slack-token", required=True, help="Slack token for outputing results")
@click.option("--bucket-name", required=True, help="Bucket name where posts are stored")
@click.option("--aws-key-id", required=True, help="AWS_KEY_ID coming from digitalocean")
@click.option(
    "--aws-secret-key", required=True, help="AWS_SECRET_KEY coming from digitalocean"
)
def main(slack_token, bucket_name, aws_key_id, aws_secret_key):
    log_format = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    rupor = SlackRupor(token=slack_token)
    staruha = Staruha(
        rupor=rupor,
        aws_access_key_id=aws_key_id,
        aws_secret_access_key=aws_secret_key,
        bucket_name=bucket_name,
    )
    staruha.run()
    return


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
