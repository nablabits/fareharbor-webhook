## base image
FROM python:3.8.6-slim-buster

## install dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y gcc && \
    apt-get clean

# Set the working directory to /app
WORKDIR /flask_app

# Copy CWD contents into the container with the same CWD
ADD . /flask_app

# Install the dependencies
RUN pip install --upgrade pip


RUN pip install -r requirements.txt

# run the command to start uWSGI
CMD ["uwsgi", "uwsgi_config.yml"]
