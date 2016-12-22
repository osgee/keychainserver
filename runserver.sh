#!/bin/bash
service apache2 restart
service mysql restart
cd ~/workspace/keychainserver
python3 manage.py runserver

