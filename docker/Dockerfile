FROM python:3.12-bookworm
LABEL maintainer='Mike Kroutikov <mkroutikov@innodata.com>'

RUN apt update; apt install -y vim sudo

COPY . /self

RUN useradd -ms /bin/bash redstork && chown -R redstork:redstork /self

# disable sudo password
RUN echo "redstork ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers

USER redstork
WORKDIR /home/redstork

RUN cd /self; BUILD_ROOT=/home/redstork PDFium_TARGET_OS=linux OS=linux PDFium_TARGET_CPU=x64 bash /self/build_scripts/build.sh

CMD [ "bash" ]

