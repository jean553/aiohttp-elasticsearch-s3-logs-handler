variable "access_key" {}
variable "secret_key" {}
variable "region" {}
variable "service_ami_id" {}
variable "key_name" {}

provider "aws" {
  access_key     = "${var.access_key}"
  secret_key     = "${var.secret_key}"
  region         = "${var.region}"
}

resource "aws_instance" "elk" {
  ami                 = "ami-0bd0cf6d" # (community) bitnami-elk-5.4.1-0-linux-debian-8-x86_64-hvm-ebs
  instance_type       = "t2.micro"
  key_name            = "${var.key_name}"

  tags {
    Name              = "tornado-kibana-logs-handler_elk"
  }
}

resource "aws_instance" "service" {
  ami                 = "${var.service_ami_id}" # (created by packer.json)
  instance_type       = "t2.micro"
  key_name            = "${var.key_name}"
  security_groups     = ["allow_ssh"]

  tags {
    Name              = "tornado-kibana-logs-handler_backend"
  }
}

resource "aws_s3_bucket" "bucket" {
  bucket              = "tornado-kibana-logs-handler"
  acl                 = "private"
}

resource "aws_security_group" "allow_ssh" {
  name                = "allow_ssh"
  description         = "allow only inbound SSH traffic"

  ingress {
    from_port         = 22
    to_port           = 22
    protocol          = "tcp"
    cidr_blocks       = ["0.0.0.0/0"]
  }

  tags {
    Name              = "allow_ssh"
  }
}
