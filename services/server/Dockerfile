# base image
FROM python:3.6.5-slim

# install netcat
RUN apt-get update && \
    apt-get -y install netcat && \
    apt-get -y install opencc && \
    apt-get install -y cron && \
    apt-get clean

# set working directory
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# add entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# add app
COPY . /usr/src/app

# set crontab
RUN cp ./crontabfile /etc/cron.d/cron-task
RUN chmod 0644 /etc/cron.d/cron-task
RUN crontab /etc/cron.d/cron-task

# run server
CMD ["/usr/src/app/entrypoint.sh"]