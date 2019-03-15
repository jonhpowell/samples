FROM docker.trebuchetdev.com/alpine:3.6

ARG INDEX
ARG INDEX_URL

RUN apk add --no-cache python3 py-pip git py-yaml && mkdir -p /opt/data-history-viewer

COPY ./app /opt/data-history-viewer/app
COPY ./requirements.txt /opt/data-history-viewer/requirements.txt

RUN pip3 install -r /opt/data-history-viewer/requirements.txt

RUN pip3 install --extra-index-url $INDEX_URL trebuchet
WORKDIR /opt/data-history-viewer

EXPOSE 8080

CMD ["python3", "-m", "app"]

