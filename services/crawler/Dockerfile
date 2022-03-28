# base image
FROM python:3.8.1-slim

# install netcat
RUN apt-get update && \
    apt-get -y install netcat && \
    apt-get clean && \
    apt-get -y install opencc && \
    apt-get -y install rsyslog

# set working directory
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# add app
COPY . /usr/src/app

# add crontab job
RUN crontab ./crontabfile

# cron
RUN cp ./crontabfile /etc/crontab
RUN touch /var/log/cron.log

RUN chmod +x ./run.sh

# run server
CMD ["bash","./run.sh"]