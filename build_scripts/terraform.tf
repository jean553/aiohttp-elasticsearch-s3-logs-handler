variable "access_key" {}
variable "secret_key" {}
variable "region" {}
variable "service_ami_id" {}

provider "aws" {
  access_key     = "${var.access_key}"
  secret_key     = "${var.secret_key}"
  region         = "${var.region}"
}

resource "aws_instance" "elk" {
  ami                 = "ami-0bd0cf6d" # (community) bitnami-elk-5.4.1-0-linux-debian-8-x86_64-hvm-ebs
  instance_type       = "t2.micro"

  tags {
    Name              = "tornado-kibana-logs-handler_elk"
  }
}

resource "aws_instance" "service" {
  ami                 = "${var.service_ami_id}" # (created by packer.json)
  instance_type       = "t2.micro"

  tags {
    Name              = "tornado-kibana-logs-handler_backend"
  }
}

resource "aws_s3_bucket" "bucket" {
  bucket              = "tornado-kibana-logs-handler"
  acl                 = "private"
}
