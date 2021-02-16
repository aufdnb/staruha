FROM python:3.8-slim-buster

WORKDIR staruha
COPY ./dist/staruha-0.1.0.tar.gz .
RUN pip install --upgrade pip
RUN pip install staruha-0.1.0.tar.gz
COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

CMD [ "./entrypoint.sh" ]