#!/bin/bash

sudo apt update -y
sudo apt install screen -y

current_path=$(pwd)
project_path="/home/ubuntu/workspace/keychainserver/"
reset_mysql_pass_sql_file="reset_mysql_pass.sql"
mysql_sql_file="mysql_sql_file.sql"
public_key_file="public_key_py.pem"
private_key_file="private_key_py.pem"
VirtualHost_File="001-keychainserver.conf"
Http_Proxy_File="http-proxy.conf"
Apache2_Sites_Enabled_Dir="/etc/apache2/sites-enabled/"
mysqld_safe_daemon="mysqld_safe_daemon"
PASSWORD_CHANGED=0
DEFAULT_PASSWORD="password"
PASSWORD=$DEFAULT_PASSWORD
SETTING_FILE=$project_path'superkeychain/settings.py'

cd $Apache2_Sites_Enabled_Dir

if [ -e $VirtualHost_File ]; then
    sudo rm -f $Apache2_Sites_Enabled_Dir$VirtualHost_File
fi

if [ -e 001-cloud9.conf ]; then
    sudo mv 001-cloud9.conf ../sites-available/001-cloud9.conf.bak
fi

sudo echo "<VirtualHost *:8080>">>$VirtualHost_File
sudo echo "ServerName https://${C9_HOSTNAME}:443">>$VirtualHost_File
sudo echo "ProxyPass / http://localhost:8000/">>$VirtualHost_File
sudo echo "ProxyPassReverse / http://localhost:8000/">>$VirtualHost_File
sudo echo "ErrorLog ${APACHE_LOG_DIR}/error.log">>$VirtualHost_File
sudo echo "CustomLog ${APACHE_LOG_DIR}/access.log combined">>$VirtualHost_File
sudo echo "</VirtualHost>">>$VirtualHost_File

cd /etc/apache2/conf-enabled

if [ -e $Http_Proxy_File ]; then
    sudo rm -f $Http_Proxy_File
fi

sudo echo "LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so">>$Http_Proxy_File
sudo echo "LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so">>$Http_Proxy_File


cd ~

echo "Would you like to reset mysql root password? (y/n) [y]"
read RESET_MYSQL_PASS

if [ "$RESET_MYSQL_PASS" == "y" ] || [ "$RESET_MYSQL_PASS" == "" ]; then
    echo "please input your mysql root password"
    read PASSWORD
    sudo service mysql stop
    echo "UPDATE user SET Password=PASSWORD('$PASSWORD') WHERE USER='root';">>$reset_mysql_pass_sql_file
    echo "FLUSH PRIVILEGES;">>$reset_mysql_pass_sql_file
    echo "CREATE DATABASE IF NOT EXISTS superkeychain;">>$reset_mysql_pass_sql_file
    sudo screen -dmS $mysqld_safe_daemon sudo mysqld_safe --skip-grant-table
    echo "Starting mysqld safe daemon..."
    sleep 3
    mysql -uroot mysql -e "source $reset_mysql_pass_sql_file"
    rm $reset_mysql_pass_sql_file
    sudo screen -X -S $mysqld_safe_daemon quit
    sed -i -E "s/('PASSWORD': ')(.*)(',)/\1$PASSWORD\3/g" $SETTING_FILE
    echo "Your mysql root password has been reset"
    echo "Please change the mysql password in keychainserver/superkeychain/settings.py consistently"
else
    sudo service mysql stop
    echo "create database superkeychain if not exists;">>$mysql_sql_file
    sudo screen -dmS $mysqld_safe_daemon sudo mysqld_safe --skip-grant-table
    echo "Starting mysqld safe daemon..."
    sleep 3
    mysql -uroot mysql -e "source $mysql_sql_file"
    rm $mysql_sql_file
    sudo screen -X -S $mysqld_safe_daemon quit
    echo "Skiped reset mysql root password"
    echo "The default mysql root password is: $DEFAULT_PASSWORD"
fi


sudo service mysql restart

echo "Would you like to reset RSA key pair? (y/n) [y]"
read RESET_RSA_KEY
if [ "$RESET_RSA_KEY" == "y" ] || [ "$RESET_RSA_KEY" == "" ]; then
    cd $project_path
    openssl genpkey -algorithm RSA -out $private_key_file -pkeyopt rsa_keygen_bits:2048
    openssl rsa -pubout -in $private_key_file -out $public_key_file
    sudo chmod go-rw $private_key_file
    echo "Your new RSA key pair has been generated, please replace the keychain client's public key file with $public_key_file, and keep the same name"
else
    echo "Skiped reset RSA key"
fi

sudo pip3 install django pymysql pillow qrcode pycrypto rsa

cd $project_path
rm -rf ./keychain/static/keychain/apps/*
mkdir -p ./keychain/static/keychain/cache/captcha/
mkdir -p ./keychain/static/keychain/cache/qrcode/
rm -rf ./keychain/migrations/0*
python3 ./manage.py makemigrations
python3 ./manage.py migrate
sudo service mysql restart
sudo service mysql status
sudo service apache2 restart
sudo service apache2 status
cd $current_path

echo "Your server is ready to running"
if [ $PASSWORD_CHANGED == 0 ]; then
    echo "Would you like to run server? (y/n) [y]"
    read RUN_SERVER
    if [ "$RUN_SERVER" == "y" ] || [ "$RUN_SERVER" == "" ]; then
        cd $project_path
        keychainserver_daemon="keychainserver_daemon"
        sudo screen -dmS $keychainserver_daemon sudo python3 manage.py runserver localhost:8000
        echo "Server run on $ screen -r ($keychainserver_daemon)"
    else
        echo "You can run keychainserver by yourself"
    fi
fi

echo "Usage:"
echo "$ cd $project_path"
echo "$ sudo python3 manage.py runserver localhost:8000"

cd $current_path