#!/bin/sh
echo 'Provisioning...'
sudo locale-gen UTF-8
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install build-essential python git python-dev python-pip -y
sudo pip install markupsafe
sudo pip install ansible

cd /vagrant/deploy
ansible-playbook main.yml -i hosts -e tools_dir=`pwd`/.. -e apps_user=vagrant

echo 'Provisioning complete'