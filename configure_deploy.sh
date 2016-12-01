current_path=$(pwd)
project_path="~/workspace/keychainserver"
reset_mysql_pass_sql_file="reset_mysql_pass.sql"
public_key_file="public_key_py.pem"
private_key_file="private_key_py.pem"
VirtualHost_File="001-keychainserver.conf"
Http_Proxy_File="http-proxy.conf"

cd /etc/apache2/sites-enabled

if [ -d $VirtualHost_File ]; then
    sudo rm -i $VirtualHost_File
fi

sudo echo "<VirtualHost *:8080>">>$VirtualHost_File
sudo echo "ServerName https://${C9_HOSTNAME}:443">>$VirtualHost_File
sudo echo "ProxyPass / http://localhost:8000/">>$VirtualHost_File
sudo echo "ProxyPassReverse / http://localhost:8000/">>$VirtualHost_File
sudo echo "ErrorLog ${APACHE_LOG_DIR}/error.log">>$VirtualHost_File
sudo echo "CustomLog ${APACHE_LOG_DIR}/access.log combined">>$VirtualHost_File
sudo echo "</VirtualHost>">>$VirtualHost_File

cd /etc/apache2/conf-enabled

if [ -d $Http_Proxy_File ]; then
    sudo rm -i $Http_Proxy_File
fi

sudo echo "LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so">>$Http_Proxy_File
sudo echo "LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so">>$Http_Proxy_File

exit

cd ~

echo "Would you like to reset mysql root password? (y/n) [y]"\
read RESET_MYSQL_PASS
if [ "$RESET_MYSQL_PASS" == "y" ] || [ "$RESET_MYSQL_PASS" == "" ]; then
    echo "please input your mysql root password"
    read PASSWORD
    sudo service mysql stop
    echo "use mysql;">>$reset_mysql_pass_sql_file
    echo "update user set Password=PASSWORD('$PASSWORD') where USER='root';">>$reset_mysql_pass_sql_file
    echo "flush privileges;">>$reset_mysql_pass_sql_file
    sudo mysqld_safe --skip-grant-table source $reset_mysql_pass_sql_file
    rm $reset_mysql_pass_sql_file
    echo "Your mysql root password has been reset"
else
    echo "Skiped reset mysql root password"
fi

sudo service mysql start

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
    
cd $project_path
rm -rf ./keychain/static/keychain/app/*
mkdir -p ./keychain/static/keychain/cache/captcha/*
mkdir -p ./keychain/static/keychain/cache/qrcode/*
rm -rf ./keychain/migrations/0*
python3 ./manage.py makemigrations
python3 ./manage.py migrate
sudo service mysql restart
sudo service apache2 restart
cd $current_path

echo "Your server is ready to running"
echo "Would you like to run server? (y/n) [y]"
read RUN_SERVER
if [ "$RUN_SERVER" == "y" ] || [ "$RUN_SERVER" == "" ]; then
    cd $project_path
    sudo python3 manage.py runserver localhost:8000
else
    echo "Usage:"
    echo "$ cd $project_path"
    echo "$ sudo python3 manage.py runserver localhost:8000"
fi
