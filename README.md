# install

install git, python-dev, python-virtualenv

`git clone blahblahblah`

`virtualenv venv`

`venv/bin/pip install -r requirements.txt`

put WU API key in the file named wu_api_key in this directory

`venv/bin/alembic upgrade head`

`venv/bin/python run_server.py`

# update

`git pull`

`venv/bin/alembic upgrade head` if database schema changed

`venv/bin/pip install -r requirements.txt` if Python dependencies changed
