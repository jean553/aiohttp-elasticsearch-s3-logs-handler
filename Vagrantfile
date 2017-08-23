# -*- mode: ruby -*-
# vi: set ft=ruby ts=2 sw=2 expandtab :

PROJECT = "tornado-kibana-logs-handler"
ENV["VAGRANT_NO_PARALLEL"] = "yes"
ENV["VAGRANT_DEFAULT_PROVIDER"] = "docker"
VAGRANTFILE_VERSION = "2"
S3_BUCKET_NAME = "tornado-kibana-logs-handler"
S3_ENDPOINT = "s3:5000"

Vagrant.configure(VAGRANTFILE_VERSION) do |config|

  environment_variables = {
    # used for 'dev' containers to have same permissions as current user
    "HOST_USER_UID" => Process.euid,
    "ENV_NAME" => "devdocker",
    "APP_PATH" => "/vagrant",
    "VIRTUAL_ENV_PATH" => "/tmp/virtual_env35",
    "PROJECT" => PROJECT,
    "ELASTICSEARCH_HOSTNAME" => "elasticsearch",

    # add your credentials here
    "AWS_ACCESS_KEY" => "dummy",
    "AWS_SECRET_KEY" => "dummy",
    "S3_BUCKET_NAME" => S3_BUCKET_NAME,
    "S3_ENDPOINT" => S3_ENDPOINT
  }

  # TODO: #27 the fake S3 bucket seems to save the files correctly
  # but throws errors (check README.md file for error details).
  config.vm.define "s3" do |s3|
    s3.vm.provider "docker" do |d|
      d.image = "jean553/docker-s3-server-dev"
      d.name = "#{PROJECT}_s3"
    end
  end

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

    app.vm.provision "ansible", type: "shell" do |ansible|
      ansible.env = environment_variables
      ansible.inline = "
        set -e
        cd $APP_PATH
        ansible-playbook build_scripts/bootstrap.yml
        echo 'done, you can now run `vagrant ssh`'
      "
    end
  end
end
