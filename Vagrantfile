# -*- mode: ruby -*-
# vi: set ft=ruby ts=2 sw=2 expandtab :

# Define project-specific constants and environment variables
# Project configuration
PROJECT = "aiohttp-elasticsearch-s3-logs-handler"
ENV["VAGRANT_NO_PARALLEL"] = "yes"
ENV["VAGRANT_DEFAULT_PROVIDER"] = "docker"
VAGRANTFILE_VERSION = "2"
S3_BUCKET_NAME = "aiohttp-elasticsearch-s3-logs-handler"
# S3 and AioHTTP configuration
S3_ENDPOINT = "s3:5000"
AIOHTTP_PORT = 8000

# Begin Vagrant configuration
Vagrant.configure(VAGRANTFILE_VERSION) do |config|

  # Set up environment variables for containers
  environment_variables = {
    # used for 'dev' containers to have same permissions as current user
    "HOST_USER_UID" => Process.euid,

    # Environment and application configuration
    "ENV_NAME" => "devdocker",
    "APP_PATH" => "/vagrant",
    "VIRTUAL_ENV_PATH" => "/tmp/virtual_env35",
    "PROJECT" => PROJECT,
    "ELASTICSEARCH_HOSTNAME" => "elasticsearch",
    "ELASTICSEARCH_PORT" => 9200,
    "AIOHTTP_PORT" => AIOHTTP_PORT,

    # AWS and S3 configuration (using dummy values for development)
    "AWS_ACCESS_KEY" => "dummy",
    "AWS_SECRET_KEY" => "dummy",
    "REGION_NAME" => "dummy",
    "S3_BUCKET_NAME" => S3_BUCKET_NAME,
    "S3_ENDPOINT" => S3_ENDPOINT
  }

  # Define and configure the S3 container
  # S3 container configuration
  config.vm.define "s3" do |s3|
    s3.vm.provider "docker" do |d|
      d.image = "jean553/docker-s3-server-dev"
      d.name = "#{PROJECT}_s3"
    end
  end

  # Define and configure the Elasticsearch container
  # Elasticsearch container configuration
  config.vm.define "elasticsearch" do |app|
    app.vm.provider "docker" do |d|
      d.image = "docker.elastic.co/elasticsearch/elasticsearch:5.4.3"
      d.name = "#{PROJECT}_elasticsearch"
      # ES looks for S3 container hostname with the bucket name
      # and custom endpoint (backups.s3)
      d.link "#{PROJECT}_s3:#{S3_BUCKET_NAME}.s3"
      d.env = {
        "http.host" => "0.0.0.0",
        "transport.host" => "127.0.0.1",
        "xpack.security.enabled" => "false",
        "path.repo" => "/tmp",
      }
    end
  end

  # Define and configure the Kibana container
  # Kibana container configuration (part of the ELK stack)
  config.vm.define "kibana" do |app|
    app.vm.provider "docker" do |d|
      d.image = "docker.elastic.co/kibana/kibana:5.4.3"
      d.name = "#{PROJECT}_kibana"
      d.link "#{PROJECT}_elasticsearch:elasticsearch"
      d.env = {
        "server.host" => "0.0.0.0",
        "xpack.security.enabled" => "false",
      }
    end
  end

  config.ssh.insert_key = true
  # Define and configure the development environment container
  # Development environment container configuration
  config.vm.define "dev", primary: true do |app|
    app.vm.provider "docker" do |d|
      d.image = "allansimon/allan-docker-dev-python"
      d.name = "#{PROJECT}_dev"
      d.link "#{PROJECT}_elasticsearch:elasticsearch"
      d.link "#{PROJECT}_s3:s3"
      d.has_ssh = true
      d.env = environment_variables
    end
    app.ssh.username = "vagrant"

    # Set up Ansible provisioning for the development environment
    # Ansible provisioning for development environment
    app.vm.provision "ansible", type: "shell" do |ansible|
      ansible.env = environment_variables
      ansible.inline = "
        set -e
        cd $APP_PATH
        ansible-playbook build_scripts/bootstrap-dev.yml
        echo 'done, you can now run `vagrant ssh`'
      "
    end
  end
end
