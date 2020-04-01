FROM python:3.7
LABEL maintainer='Mike Kroutikov <mkroutikov@innodata.com>'

COPY . /self

RUN bash /self/build_scripts/build.sh

WORKDIR /pdfium/pdfium_red

CMD [ "bash" ]
