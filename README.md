# keychainserver

### configure apache2

in /etc/apache2/sites-enabled create new config file 001-keychainserver.conf

    <VirtualHost *:8080>
        ServerName https://${C9_HOSTNAME}:443
        ProxyPass / http://localhost:8000/
        ProxyPassReverse / http://localhost:8000/
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>
    
in /etc/apache2/conf-enabled create new config file http-proxy.conf

    LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so
    LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so

restart Apache2

    $ service apache2 restart

### configure database 
restrat Mysql

    $ service mysql restart

    $ mysql -uroot -p
    
create database

    mysql > create database superkeychain;  

install python3 dependencies

    $ sudo pip3 install django pymysql qrcode pycrypto rsa

init database

    $ sudo python3 manage.py makemigrations
    $ sudo python3 manage.py migrate

run server

    $ sudo python3 manage.py runserver localhost:8000

### advanced options and issues

    $ sudo apt-get install uwsgi 

#### proxy on https

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

#### opnvpn init:

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

#### add modules to conf-enabled/

    LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so  
    LoadModule proxy_connect_module /usr/lib/apache2/modules/mod_proxy_connect.so  
    LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so  
    LoadModule proxy_ftp_module /usr/lib/apache2/modules/mod_proxy_ftp.so  
    LoadModule rewrite_module /usr/lib/apache2/modules/mod_rewrite.so  
    LoadModule ssl_module /usr/lib/apache2/modules/mod_ssl.so

#### https:

##### 1）generate Apache's RSA private key server.key：

    $ openssl genrsa -out server.key 2048

##### 2）sign request server.csr：

    $ openssl req -new -out server.csr -key server.key

ps：infos about country，province（city），department，name，email，password...

##### 3）sign to webiste server certificate by CA：
cmd1-generate CA private key：

    $ openssl genrsa -out ca.key 1024

cmd2-use CA private key to generate CA's self-sign certificate：

    $ openssl req -new -x509 -days 365 -key ca.key -out ca.crt 

ps: infos as privious

cmd3-sign to webiste server certificate by CA：
create folder demoCA in /bin，create file index.txt, serial and folder newcerts inside，the file serial's content is 01，while others kept empty。
then use openssl ca to generate server.crt certificate

    $ mkdir demoCA
    $ cd demoCA
    $ echo ''>index.txt
    $ echo '01'>serial
    $ mkdir newcerts
    $ openssl ca -in server.csr -out server.crt -cert ca.crt -keyfile ca.key

#### 4）cp files：
copy server.crt，server.key，ca.key to apache2's conf file folder

    ref: <a href="http://openwares.net/misc/pki_key_pair_certificate.html">reffrence</a>
      
### issues

#### apache start failure
Apache start failure：
the requested operation has failed
Syntax error on line 487 of D:/Java/Apache2.2/conf/httpd.conf:
Invalid command 'ProxyPass', perhaps misspelled or defined by a module not inclu
ded in the server configuration
Note the errors or messages above, and press the key to exit. 0....
原因：需要在http.conf文件中配置以下模块：
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so

#### reset mysql password

    miui:~ $ sudo service mysql stop                                                                                                      [ OK ] 
    miui:~ $ sudo mysqld_safe --skip-grant-table
    miui:~/workspace $ mysql -uroot mysql
    mysql> show databases;
    mysql> use mysql;
    mysql> show tables;
    mysql> update user set Password=PASSWORD('password') where USER='root';                                                                                
    mysql> flush privileges;                                                                                                                               

    miui:~ $ sudo service mysql start
    miui:~/workspace/superkeychain $ python3  manage.py runserver localhost:8000
    miui:~/workspace $ service apache2 restart
