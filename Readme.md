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
* Setup new password
* Remove anonymous users
* Disallow root login remotely
* Remove test database and access to it
* Reload privilege tables

Modify config file:
```sh
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```
* Configure bind address as **127.0.0.1,172.17.0.1**

Run mysql and do some configurations:
```sh
mysql -u root -p
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
 GRANT ALL PRIVILEGES ON *.* TO 'username'@'%' WITH GRANT OPTION;FLUSH PRIVILEGES;
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
* add TelegramBot Token to conf.ini
* add mysql connection string to conf.ini
```sh
python3 ./main.py
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

```
