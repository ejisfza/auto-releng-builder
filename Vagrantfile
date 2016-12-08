# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
# Require YAML module
require 'yaml'

# Read file yaml with configuration
environment = YAML.load_file("scripts/conf-env.yml")

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.synced_folder "./builder", "/builder"
  config.vm.synced_folder "./scripts", "/scripts"

# Iterate through entries in YAML file
  environment.each do |env|
      env["topology"].each do |servers|
          config.ssh.username = "centos"
          config.ssh.password = "centos"
          config.vm.define servers["name"] do |srv|
              srv.vm.box = servers["box_name"]
              srv.vm.box_url = servers["box_url"]
              srv.vm.hostname = servers["hostname"]
              srv.vm.network "private_network", ip: servers["ip"]
              srv.vm.provider :virtualbox do |vb|
                  vb.name = servers["name"] + "_" + env["name"]
                  vb.cpus = servers["cpu_cores"]
                  vb.memory = servers["memory"]
              end
              servers["provision"].each do |script|
                  srv.vm.provision :shell, :inline => script
              end
          end
      end
  end
end

