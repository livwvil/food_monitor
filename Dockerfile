FROM python

WORKDIR /app

COPY . .

RUN pip install pyTelegramBotAPI

RUN pip install pymysql

RUN pip install peewee

RUN pip install cryptography

RUN apt update -y

RUN apt upgrade -y

RUN apt install -y iproute2

ENV TZ=Europe/Moscow

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD ["sh", "starter.sh"]