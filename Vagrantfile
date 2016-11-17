# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "private_network", type: "dhcp"

  config.vm.provider "virtualbox" do |vb|
     vb.memory = "2048"
     #vb.gui = true
  end

  config.vm.provision :shell, :path => "provision.sh"
end