variable "access_key" {}
variable "secret_key" {}
variable "region" {}
variable "backend_ami_id" {}
variable "es_ami_id" {}
variable "kibana_ami_id" {}
variable "worker_ami_id" {}
variable "key_name" {}

provider "aws" {
  access_key     = "${var.access_key}"
  secret_key     = "${var.secret_key}"
  region         = "${var.region}"
}

resource "aws_instance" "worker" {
  ami                 = "${var.worker_ami_id}" # created by packer_es.json
  instance_type       = "t2.micro"
  key_name            = "${var.key_name}"
  security_groups     = [
                            "${aws_security_group.allow_ssh.id}",
                            "${aws_security_group.allow_all_outbound.id}"
                        ]
  subnet_id           = "${aws_subnet.vpc_subnet.id}"
  private_ip          = "10.0.0.13"

  tags {
    Name              = "aiohttp-elasticsearch-s3-logs-handler_worker"
  }
}

resource "aws_instance" "kibana" {
  ami                 = "${var.kibana_ami_id}" # created by packer_es.json
  instance_type       = "t2.micro"
  key_name            = "${var.key_name}"
  security_groups     = [
                            "${aws_security_group.allow_ssh.id}",
                            "${aws_security_group.allow_kibana.id}",
                            "${aws_security_group.allow_all_outbound.id}"
                        ]
  subnet_id           = "${aws_subnet.vpc_subnet.id}"
  private_ip          = "10.0.0.12"

  tags {
    Name              = "aiohttp-elasticsearch-s3-logs-handler_kibana"
  }
}

resource "aws_instance" "es" {
  ami                 = "${var.es_ami_id}" # created by packer_es.json
  instance_type       = "t2.medium" # Java 8 requires 2 Gb of RAM
  key_name            = "${var.key_name}"
  security_groups     = [
                            "${aws_security_group.allow_ssh.id}",
                            "${aws_security_group.allow_elasticsearch.id}",
                            "${aws_security_group.allow_all_outbound.id}"
                        ]
  subnet_id           = "${aws_subnet.vpc_subnet.id}"
  private_ip          = "10.0.0.11"

  tags {
    Name              = "aiohttp-elasticsearch-s3-logs-handler_es"
  }
}

resource "aws_instance" "backend" {
  ami                 = "${var.backend_ami_id}" # created by packer_backend.json
  instance_type       = "t2.micro"
  key_name            = "${var.key_name}"
  security_groups     = [
                            "${aws_security_group.allow_ssh.id}",
                            "${aws_security_group.allow_http.id}",
                            "${aws_security_group.allow_all_outbound.id}"
                        ]
  subnet_id           = "${aws_subnet.vpc_subnet.id}"
  private_ip          = "10.0.0.10"

  tags {
    Name              = "aiohttp-elasticsearch-s3-logs-handler_backend"
  }
}

resource "aws_s3_bucket" "bucket" {
  bucket              = "aiohttp-elasticsearch-s3-logs-handler"
  acl                 = "private"
}

resource "aws_vpc" "vpc" {

  cidr_block          = "10.0.0.0/28"

  tags {
    Name              = "aiohttp-elasticsearch-s3-logs-handler_vpc"
  }
}

resource "aws_subnet" "vpc_subnet" {

  vpc_id              = "${aws_vpc.vpc.id}"
  cidr_block          = "10.0.0.0/28"

  tags {
    Name              = "aiohttp-elasticsearch-s3-logs-handler_vpc_subnet"
  }
}

resource "aws_internet_gateway" "vpc_gateway" {

  vpc_id              = "${aws_vpc.vpc.id}"

  tags {
    Name              = "aiohttp-elasticsearch-s3-logs-handler_vpc_gateway"
  }
}

resource "aws_default_route_table" "vpc_default_route_table" {

  default_route_table_id = "${aws_vpc.vpc.default_route_table_id}"

  route {
    cidr_block        = "0.0.0.0/0"
    gateway_id        = "${aws_internet_gateway.vpc_gateway.id}"
  }

  tags {
    Name              = "aiohttp-elasticsearch-s3-logs-handler_vpc_default_route_table"
  }
}

resource "aws_eip" "backend_eip" {
  instance            = "${aws_instance.backend.id}"
  vpc                 = true
}

resource "aws_eip" "es_eip" {
  instance            = "${aws_instance.es.id}"
  vpc                 = true
}

resource "aws_eip" "kibana_eip" {
  instance            = "${aws_instance.kibana.id}"
  vpc                 = true
}

resource "aws_eip" "worker_eip" {
  instance            = "${aws_instance.worker.id}"
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

    # SSH connection can be performed from anywhere
    cidr_blocks       = ["0.0.0.0/0"]
  }

  tags {
    Name              = "allow_ssh"
  }
}

resource "aws_security_group" "allow_http" {
  name                = "allow_http"
  description         = "allow only inbound HTTP traffic"
  vpc_id              = "${aws_vpc.vpc.id}"

  ingress {
    from_port         = 80
    to_port           = 80
    protocol          = "tcp"

    # HTTP connection can be performed from anywhere
    cidr_blocks       = ["0.0.0.0/0"]
  }

  tags {
    Name              = "allow_http"
  }
}

resource "aws_security_group" "allow_elasticsearch" {
  name                = "allow_elasticsearch"
  description         = "allow only inbound elasticsearch traffic"
  vpc_id              = "${aws_vpc.vpc.id}"

  ingress {
    from_port         = 9200
    to_port           = 9200
    protocol          = "tcp"

    # Elasticsearch actions can only be performed
    # from the backend, Kibana and the worker
    cidr_blocks       = [
                            "10.0.0.10/32",
                            "10.0.0.12/32",
                            "10.0.0.13/32"
                        ]
  }

  tags {
    Name              = "allow_elasticsearch"
  }
}

resource "aws_security_group" "allow_kibana" {
  name                = "allow_kibana"
  description         = "allow only inbound kibana traffic"
  vpc_id              = "${aws_vpc.vpc.id}"

  ingress {
    from_port         = 5601
    to_port           = 5601
    protocol          = "tcp"

    # Kibana connections can be performed from anywhere
    cidr_blocks       = ["0.0.0.0/0"]
  }

  tags {
    Name              = "allow_kibana"
  }
}

resource "aws_security_group" "allow_all_outbound" {
  name                = "allow_all_outbound"
  description         = "allow all outbound traffic"
  vpc_id              = "${aws_vpc.vpc.id}"

  egress {
    from_port         = 0
    to_port           = 0
    protocol          = "-1" # all
    cidr_blocks       = ["0.0.0.0/0"]
  }

  tags {
    Name              = "allow_all_outbound"
  }
}
