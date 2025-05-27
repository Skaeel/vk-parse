FROM python:3.9

COPY requirements.txt .
RUN pip3 install --user -r requirements.txt

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1

ENV APP_HOME /usr/src/app/src
WORKDIR $APP_HOME

COPY ./src $APP_HOME/

CMD ["python3", "main.py"]