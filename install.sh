#!/bin/bash

echo "type your user password - it should be in the sudoers group"
sudo apt-get install python-dev python-setuptools python-pip
virtualenv venv-desugaala
source venv-desugaala/bin/activate
git clone https://github.com/diraol/urna-eletronica.git
cd urna-eletronica
pip install -r requirements.txt
pip install pysqlite2 # hint: psycopg2 or MySQL-python
#cp desugaala/settings.py.dist desugaala/settings.py
#vim desugaala/settings.py
./manage.py syncdb
./manage.py migrate
./manage.py loaddata vote desugaala2012
./manage.py run_gunicorn
