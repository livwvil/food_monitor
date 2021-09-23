# Install MySQL server
sudo apt install mysql-server

sudo mysql_secure_installation

* Press y|Y for Yes, any other key for No:
* y
* Please enter 0 = LOW, 1 = MEDIUM and 2 = STRONG:
* 0
* New password: 
* qwerty1121
* Re-enter new password: 
* qwerty1121
* Do you wish to continue with the password provided?(Press y|Y for Yes, any other key for No) :
* y
* Remove anonymous users? (Press y|Y for Yes, any other key for No) :
* y
* Disallow root login remotely? (Press y|Y for Yes, any other key for No) :
* n
* Remove test database and access to it? (Press y|Y for Yes, any other key for No) :
* y
* Reload privilege tables now? (Press y|Y for Yes, any other key for No) :
* y
* sudo mysql

```
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
comment bind-address
```

```
* SELECT user,authentication_string,plugin,host FROM mysql.user;
* ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'qwerty1121';
* SELECT user,authentication_string,plugin,host FROM mysql.user;
* FLUSH PRIVILEGES;
```

```
 CREATE USER 'notrootbutadmin'@'localhost' IDENTIFIED BY 'SerhEo238*';GRANT ALL PRIVILEGES ON *.* TO 'notrootbutadmin'@'localhost' WITH GRANT OPTION;CREATE USER 'notrootbutadmin'@'%' IDENTIFIED BY 'SerhEo238*';GRANT ALL PRIVILEGES ON *.* TO 'notrootbutadmin'@'%' WITH GRANT OPTION;FLUSH PRIVILEGES;
```

* sudo systemctl restart mysql

```
scp src/some.sql root@ip:dst
mysql -u root -p < some.sql
```


# Install dependencies
pip install pyTelegramBotAPI

pip install pymysql

pip install peewee

# Run
add TelegramBot Token to conf.ini

python3 ./main.py

# Help
* sudo docker run -it image_id bash
* sudo docker exec -it container_id bash
* mysql -u root -p
* systemctl status mysql.service
* sudo systemctl start mysql
* mysqladmin -p -u root version


