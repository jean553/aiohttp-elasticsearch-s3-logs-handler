provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region     = "${var.region}"
}

resource "aws_instance" "elk" {
  ami                 = "ami-0bd0cf6d" # (community) bitnami-elk-5.4.1-0-linux-debian-8-x86_64-hvm-ebs
  instance_type       = "t2.micro"
}

resource "aws_instance" "service" {
  ami                 = "ami-440d4837" # (community) debian-stretch-amd64-hvm-2016-09-23-08-48-ebs
  instance_type       = "t2.micro"
}
