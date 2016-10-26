# install

install ansible

    cd deploy

Create file ~/.my.cnf and add following lines in it and replace mysqluser & mysqlpass values.

    [client]
    user=mysqluser
    password=mysqlpass

For safety, make this file readable to you only by running chmod 0600 ~/.my.cnf

    ansible-playbook main.yml -i hosts -e tools_dir=`pwd`/.. --ask-sudo-pass

enter you user pass

put WU API key in the file named wu_api_key in this directory

put Google maps API key in the file named gmap_api_key in this directory

    FLASK_ENV=PRODUCTION venv/bin/python run_server.py in screen session

    FLASK_ENV=PRODUCTION venv/bin/rqworker in another screen session

    venv/bin/alembic stamp head

# update

    git pull

    venv/bin/alembic upgrade head if database schema changed

    venv/bin/pip install -r requirements.txt if Python dependencies changed

restart both run_server.py and rqworker
