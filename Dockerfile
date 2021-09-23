FROM python

WORKDIR /app

COPY ./src/main.py .

COPY ./src/conf.ini .

COPY ./src/starter.sh .

RUN pip install pyTelegramBotAPI

RUN pip install pymysql

RUN pip install peewee

RUN pip install cryptography

RUN apt update

RUN apt upgrade

RUN apt install -y iproute2

CMD ["sh", "starter.sh"]