FROM python:3.5.1
MAINTAINER Waylon Wang <waylon.act@gmail.com>

COPY *.py ./
COPY msg_src_adapters msg_src_adapters
COPY filters filters
COPY commands commands
COPY nl_processors nl_processors
COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update \
    && apt-get install -y libav-tools \
    && apt-get install -y net-tools \
    && apt-get install -y iputils-ping \
    && apt-get install -y vim \
    && rm -rf /var/lib/apt/lists/*

CMD python app.py