rm -rf ./keychain/static
mkdir -p ./keychain/static/keychain/cache/captcha
mkdir -p ./keychain/static/keychain/cache/qrcode
rm
rm -rf ./keychain/migrations/0*
python3 ./manage.py makemigrations
python3 ./manage.py migrate
service mysql restart
service apache2 restart
