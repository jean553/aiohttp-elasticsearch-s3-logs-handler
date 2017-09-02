provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region     = "${var.region}"
}

resource "aws_instance" "elasticsearch" {
  ami                 = "ami-0f4fb276" # (community) bitnami-elasticsearch-5.5.2-0-linux-debian-8-x86_64-ebs
  instance_type       = "t1.micro"
}
