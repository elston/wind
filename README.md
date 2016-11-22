# Install

    sudo apt-get update -y
    sudo apt-get upgrade -y
    sudo apt-get install build-essential python git python-dev libffi-dev libssl-dev python-pip -y
    sudo pip install markupsafe
    sudo pip install ansible

Clone git repository. 

    git clone https://testing12@bitbucket.org/firsttier/wind.git

Go to the repository working directory. `cd wind`

    cd deploy

    ansible-playbook main.yml -i hosts -e tools_dir=`pwd`/.. --ask-sudo-pass

Enter you user pass.

    cd ..
    env/bin/alembic stamp head

Put WU API key in the file named wu_api_key in this directory.

Put Google maps API key in the file named gmap_api_key in this directory.

**Production environment is ready**

## Run test environment

in screen session

    FLASK_ENV=PRODUCTION venv/bin/python run_server.py

in another screen session

    FLASK_ENV=PRODUCTION venv/bin/rqworker

# Update

Go to the repository working directory.

    git pull

if database schema changed

    env/bin/alembic upgrade head

if Python dependencies changed

    env/bin/pip install -r requirements.txt

## Production environment

    service wind-gunicorn restart
    service wind-rqworker restart

## Test environment

restart both run_server.py and rqworker