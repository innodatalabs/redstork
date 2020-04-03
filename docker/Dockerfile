FROM python:3.8-buster
LABEL maintainer='Mike Kroutikov <mkroutikov@innodata.com>'

COPY . /self

RUN bash /self/build_scripts/build.sh

WORKDIR /pdfium/redstork

CMD [ "bash" ]

