variable "access_key" {}
variable "secret_key" {}
variable "region" {}
variable "backend_ami_id" {}
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
  subnet_id           = "${aws_subnet.vpc_subnet.id}"

  tags {
    Name              = "tornado-kibana-logs-handler_elk"
  }
}

resource "aws_instance" "backend" {
  ami                 = "${var.backend_ami_id}" # (created by packer.json)
  instance_type       = "t2.micro"
  key_name            = "${var.key_name}"
  security_groups     = ["${aws_security_group.allow_ssh.id}"]
  subnet_id           = "${aws_subnet.vpc_subnet.id}"

  tags {
    Name              = "tornado-kibana-logs-handler_backend"
  }
}

resource "aws_s3_bucket" "bucket" {
  bucket              = "tornado-kibana-logs-handler"
  acl                 = "private"
}

resource "aws_vpc" "vpc" {

  cidr_block          = "10.0.0.0/28"

  tags {
    Name              = "tornado-kibana-logs-handler_vpc"
  }
}

resource "aws_subnet" "vpc_subnet" {

  vpc_id              = "${aws_vpc.vpc.id}"
  cidr_block          = "10.0.0.0/28"

  tags {
    Name              = "tornado-kibana-logs-handler_vpc_subnet"
  }
}

resource "aws_internet_gateway" "vpc_gateway" {

  vpc_id              = "${aws_vpc.vpc.id}"

  tags {
    Name              = "tornado-kibana-logs-handler_vpc_gateway"
  }
}

resource "aws_route_table" "vpc_route_table" {
  
  vpc_id              = "${aws_vpc.vpc.id}"

  route {
    cidr_block        = "0.0.0.0/0"
    gateway_id        = "${aws_internet_gateway.vpc_gateway.id}"
  }

  tags {
    Name              = "tornado-kibana-logs-handler_vpc_route_table"
  }
}

resource "aws_eip" "backend_eip" {

  instance            = "${aws_instance.backend.id}"
  vpc                 = true
}

resource "aws_security_group" "allow_ssh" {
  name                = "allow_ssh"
  description         = "allow only inbound SSH traffic"
  vpc_id              = "${aws_vpc.vpc.id}"

  ingress {
    from_port         = 22
    to_port           = 22
    protocol          = "tcp"

    #NOTE: bad practice, a bastion is better
    cidr_blocks       = ["0.0.0.0/0"]
  }

  tags {
    Name              = "allow_ssh"
  }
}
