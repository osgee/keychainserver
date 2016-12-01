current_path=$(pwd)
project_path="~/workspace/keychainserver"
reset_mysql_pass_sql_file="reset_mysql_pass.sql"
public_key_file="public_key_py.pem"
private_key_file="private_key_py.pem"
sudo su
cd /etc/apache2/sites-enabled

if [ -d 001-keychainserver.conf ]; then
    rm 001-keychainserver.conf
fi

echo "<VirtualHost *:8080>">>001-keychainserver.conf
echo "ServerName https://${C9_HOSTNAME}:443">>001-keychainserver.conf
echo "ProxyPass / http://localhost:8000/">>001-keychainserver.conf
echo "ProxyPassReverse / http://localhost:8000/">>001-keychainserver.conf
echo "ErrorLog ${APACHE_LOG_DIR}/error.log">>001-keychainserver.conf
echo "CustomLog ${APACHE_LOG_DIR}/access.log combined">>001-keychainserver.conf
echo "</VirtualHost>">>001-keychainserver.conf

cd /etc/apache2/conf-enabled

if [ -d http-proxy.conf ]; then
    rm http-proxy.conf
fi

echo "LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so"
echo "LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so"

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
service mysql restart
service apache2 restart
cd $current_path
