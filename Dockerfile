FROM ubuntu:latest
LABEL authors="sachok_42"

ENTRYPOINT ["top", "-b"]