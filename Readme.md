# Install dependencies

## Python dependencies

Install packages

```sh
pip install pyTelegramBotAPI
pip install pymysql
pip install peewee
```

## MySQL server

Install MySQL server

```sh
sudo apt install mysql-server
```

Run this command and:

```sh
sudo mysql_secure_installation
```

- Setup new password
- Remove anonymous users
- Disallow root login remotely
- Remove test database and access to it
- Reload privilege tables

Modify config file:

```sh
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

- Configure bind address as **127.0.0.1,172.17.0.1**

Run mysql and do some configurations:

```sh
mysql -u root -p
```

Disallow root login remotely

```sql
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
FLUSH PRIVILEGES;
```

Setup root login by password

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'your_password';
FLUSH PRIVILEGES;
# Selfcheck
# SELECT user,authentication_string,plugin,host FROM mysql.user;
```

Or create new user

```sql
 CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
 GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost' WITH GRANT OPTION;

 CREATE USER 'username'@'%' IDENTIFIED BY 'password';
 GRANT ALL PRIVILEGES ON *.* TO 'username'@'%' WITH GRANT OPTION;
 FLUSH PRIVILEGES;
```

Enable access by password (for MySQL Front)

```sql
ALTER USER 'username'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
FLUSH PRIVILEGES;
```

Restart mysql

```sh
sudo systemctl restart mysql
```

Create or copy database

```sh
# copy database from host to remote server by ssh
scp path/some.sql root@ip:dst_path

# run sql script
mysql -u root -p < some.sql
```

# Run

- add TelegramBot Token to conf.ini
- add mysql connection string to conf.ini

```sh
python3 ./main.py
```

# CMD Useful scripts

## Import file

```cmd
@echo off
set file=path/to/default/file
set /p file=What file? (press Enter to get %file% as default):
cmd /C scp -i path/to/ssh_key user@ip:%file% ./
```

## Export file (drag'n'drop)

```cmd
@echo off
cmd /C scp -i path/to/ssh_key %1 user@ip:/path/to/destination/folder
```

## Connect server

```cmd
@echo off
cmd /C ssh -i path/to/ssh_key user@ip
```

# Useful commands

```sh
# interactive docker image bash session
sudo docker run --rm -it image_id bash

# interactive docker container bash session
sudo docker exec -it container_id bash

# other
mysqladmin -p -u root version
systemctl status mysql.service
sudo systemctl start mysql

# MySQL import/export
mysql -u root -p < backup.sql
mysqldump -u root -p food_monitor_prod > backup.sql

# monitor port connections
tcpdump -i any port 3333
```
