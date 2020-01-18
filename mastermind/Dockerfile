FROM python:latest
MAINTAINER Albert Lopez Alcacer <alcacer.la.1001@gmail.com>

# Install the os requirements
RUN apt-get update && apt-get install -qq -y build-essential libpq-dev gcc python-setuptools python-dev libffi-dev libpango1.0-0 libcairo2 vim netcat git cron
RUN easy_install pip && pip install --upgrade pip

# Following commands will be issued from this path
WORKDIR /data/mastermind

# Install requirements first to avoid invalidating this cache layer
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Wait for database and run gunicorn server
ADD config/run.sh /run.sh
ADD config/wait-for.sh /wait-for.sh
RUN chmod +x /run.sh
RUN chmod +x /wait-for.sh
CMD /run.sh
