# keychainserver

在/etc/apache2/sites-enabled 下新建一个文件 mysites.conf
<VirtualHost *:8080>
    ServerName https://${C9_HOSTNAME}:443
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
    #ProxyPass / http://localhost:8000/
    #ProxyPassReverse / http://localhost:8000/
</VirtualHost>
    
在/etc/apache2/conf-enabled 下新建一个文件 http.conf
LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so
LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so

$ service apache2 restart

$ service mysql restart

$ mysql -uroot -p

mysql > create database superkeychain;

$ sudo pip3 install django pymysql qrcode pycrypto rsa

$ sudo python3 manage.py makemigrations

$ sudo python3 manage.py migrate

$ sudo python3 manage.py runserver localhost:8000

#advanced options and issues

$ sudo apt-get install uwsgi 

代理https

<VirtualHost *:80>  
    <IfModule mod_proxy.c>  
        ProxyRequests Off  
        SSLProxyEngine on  
    </IfModule>  
    ServerName 127.0.0.1:80  
    ServerAdmin webmaster@localhost  
    ProxyPass / https://login.taobao.com/  
    ProxyPassReverse / https://login.taobao.com/  
</VirtualHost> 

opnvpn init:

sudo /usr/local/openvpn_as/bin/ovpn-init

<VirtualHost *:8080>
    ServerName https://${C9_HOSTNAME}:443
    ProxyRequests Off
    SSLProxyEngine on
    ProxyPass /google/ https://www.google.ca:443/
    ProxyPassReverse /google/ https://www.google.ca:443/
    LogLevel info
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

conf-enabled/

LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so  
LoadModule proxy_connect_module /usr/lib/apache2/modules/mod_proxy_connect.so  
LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so  
LoadModule proxy_ftp_module /usr/lib/apache2/modules/mod_proxy_ftp.so  
LoadModule rewrite_module /usr/lib/apache2/modules/mod_rewrite.so  
LoadModule ssl_module /usr/lib/apache2/modules/mod_ssl.so

https:

1）生成服务器Apache的RSA私钥server.key：

      命令：openssl genrsa -out server.key 1024

2）生成签署申请server.csr：

      命令：openssl req -new -out server.csr -key server.key -config ..\conf\openssl.cnf 

      注：这一步会需要输入，国家，地区（省市），公司，部门，姓名，邮箱的信息，还有一个密码。我胡填的，但是好像也没用，简单易记就行。

3）通过CA为网站服务器签署证书：

      命令1-生成CA私钥：openssl genrsa -out ca.key 1024

      命令2-利用CA私钥生成CA的自签署证书：openssl req -new -x509 -days 365 -key ca.key -out ca.crt -config ..\conf\openssl.cnf

           注：这步要填写信息，同上

      命令3-CA为网站服务器签署证书：

           在bin目录下创建demoCA，里面创建文件index.txt和serial以及文件夹newcerts，serial内容为01，其他为空。再执行下面的命令，生成server.crt文件

           openssl ca -in server.csr -out server.crt -cert ca.crt -keyfile ca.key -config ..\conf\openssl.cnf

4）复制文件：

      将server.crt，server.key，ca.key复制到apache的conf文件夹下。原因：待查。
      
      http://openwares.net/misc/pki_key_pair_certificate.html
      
issues

apache 启动失败
Apache启动报错：
the requested operation has failed
Syntax error on line 487 of D:/Java/Apache2.2/conf/httpd.conf:
Invalid command 'ProxyPass', perhaps misspelled or defined by a module not inclu
ded in the server configuration
Note the errors or messages above, and press the key to exit. 0....
原因：需要在http.conf文件中配置以下模块：
#LoadModule proxy_module modules/mod_proxy.so
#LoadModule proxy_http_module modules/mod_proxy_http.so
改为：
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so


# reset mysql password
miui:~ $ sudo service mysql stop
 * Stopping MySQL database server mysqld                                                                                                        [ OK ] 
miui:~ $ sudo mysqld_safe --skip-grant-table
160323 04:45:31 mysqld_safe Can't log to error log and syslog at the same time.  Remove all --log-error configuration options for --syslog to take effect.
160323 04:45:31 mysqld_safe Logging to '/var/log/mysql/error.log'.
160323 04:45:31 mysqld_safe Starting mysqld daemon with databases from /var/lib/mysql


miui:~/workspace $ mysql -uroot mysql
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 1
Server version: 5.5.47-0ubuntu0.14.04.1 (Ubuntu)

Copyright (c) 2000, 2015, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| phpmyadmin         |
| superkeychain      |
+--------------------+
5 rows in set (0.00 sec)

mysql> use mysql;
Database changed
mysql> show tables;
+---------------------------+
| Tables_in_mysql           |
+---------------------------+
| columns_priv              |
| db                        |
| event                     |
| func                      |
| general_log               |
| help_category             |
| help_keyword              |
| help_relation             |
| help_topic                |
| host                      |
| ndb_binlog_index          |
| plugin                    |
| proc                      |
| procs_priv                |
| proxies_priv              |
| servers                   |
| slow_log                  |
| tables_priv               |
| time_zone                 |
| time_zone_leap_second     |
| time_zone_name            |
| time_zone_transition      |
| time_zone_transition_type |
| user                      |
+---------------------------+
24 rows in set (0.00 sec)
mysql> update user set Password=PASSWORD('ft123456') where USER='root';                                                                                
Query OK, 0 rows affected (0.01 sec)
Rows matched: 4  Changed: 0  Warnings: 0

mysql> flush privileges;                                                                                                                               
Query OK, 0 rows affected (0.00 sec)

miui:~ $ sudo service mysql start
 * Starting MySQL database server mysqld       
 * 
 miui:~/workspace/superkeychain $ python3  manage.py runserver localhost:8000

miui:~/workspace $ service apache2 restart
 * Restarting web server apache2             
 * AH00558: apache2: Could not reliably determine the server's fully qualified domain name, 
 * using 172.17.4.247. Set the 'ServerName' directive globally to suppress this message