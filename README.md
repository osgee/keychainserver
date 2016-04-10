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

### advanced options and issues

    $ sudo apt-get install uwsgi 

#### 代理https

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

##### 1）生成服务器Apache的RSA私钥server.key：

    $ openssl genrsa -out server.key 1024

##### 2）生成签署申请server.csr：

    $ openssl req -new -out server.csr -key server.key -config ..\conf\openssl.cnf 

注：这一步会需要输入，国家，地区（省市），公司，部门，姓名，邮箱的信息，还有一个密码。

##### 3）通过CA为网站服务器签署证书：
命令1-生成CA私钥：

    $ openssl genrsa -out ca.key 1024

命令2-利用CA私钥生成CA的自签署证书：

    $ openssl req -new -x509 -days 365 -key ca.key -out ca.crt -config ..\conf\openssl.cnf

注：这步要填写信息，同上

命令3-CA为网站服务器签署证书：
在bin目录下创建demoCA，里面创建文件index.txt和serial以及文件夹newcerts，serial内容为01，其他为空。再执行下面的命令，生成server.crt文件

    $ openssl ca -in server.csr -out server.crt -cert ca.crt -keyfile ca.key -config ..\conf\openssl.cnf

#### 4）复制文件：
将server.crt，server.key，ca.key复制到apache的conf文件夹下。

    ref: <a href="http://openwares.net/misc/pki_key_pair_certificate.html">reffrence</a>
      
### issues

#### apache 启动失败
Apache启动报错：
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
