# install

    sudo apt-get update -y
    sudo apt-get upgrade -y
    sudo apt-get install build-essential python git python-dev python-pip -y
    sudo pip install markupsafe
    sudo pip install ansible 
    
    git pull https://testing12@bitbucket.org/firsttier/wind.git
    cd deploy

    ansible-playbook main.yml -i hosts -e tools_dir=`pwd`/.. --ask-sudo-pass

enter you user pass

put WU API key in the file named wu_api_key in this directory

put Google maps API key in the file named gmap_api_key in this directory

production environment is ready

## run test environment

    FLASK_ENV=PRODUCTION venv/bin/python run_server.py in screen session

    FLASK_ENV=PRODUCTION venv/bin/rqworker in another screen session

    venv/bin/alembic stamp head

# update

    git pull

    venv/bin/alembic upgrade head if database schema changed

    venv/bin/pip install -r requirements.txt if Python dependencies changed

## production environment

    service wind-gunicorn restart
    service wind-rqworker restart

## test environment

restart both run_server.py and rqworker