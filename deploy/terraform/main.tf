# 香港地域可用区与 Ubuntu 22.04 镜像查询
data "alicloud_zones" "default" {
  available_resource_creation = "Instance"
  available_instance_type     = var.instance_type
}

data "alicloud_images" "ubuntu" {
  owners      = "system"
  name_regex  = "^ubuntu_22_04_x64"
  most_recent = true
}

# --- 网络 ---

resource "alicloud_vpc" "main" {
  vpc_name   = "poem-vpc"
  cidr_block = "10.0.0.0/16"
}

resource "alicloud_vswitch" "main" {
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.0.1.0/24"
  zone_id      = data.alicloud_zones.default.zones[0].id
  vswitch_name = "poem-vswitch"
}

# --- 安全组：放行 22/80/443 ---

resource "alicloud_security_group" "main" {
  security_group_name = "poem-sg"
  vpc_id              = alicloud_vpc.main.id
}

resource "alicloud_security_group_rule" "ssh" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "22/22"
  security_group_id = alicloud_security_group.main.id
  cidr_ip           = var.ssh_cidr
}

resource "alicloud_security_group_rule" "http" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "80/80"
  security_group_id = alicloud_security_group.main.id
  cidr_ip           = "0.0.0.0/0"
}

resource "alicloud_security_group_rule" "https" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "443/443"
  security_group_id = alicloud_security_group.main.id
  cidr_ip           = "0.0.0.0/0"
}

# --- ECS 实例 ---

resource "alicloud_instance" "main" {
  instance_name        = "poem-comunity"
  instance_type        = var.instance_type
  image_id             = data.alicloud_images.ubuntu.images[0].id
  security_groups      = [alicloud_security_group.main.id]
  vswitch_id           = alicloud_vswitch.main.id
  password             = var.instance_password

  system_disk_category = "cloud_essd"
  system_disk_size     = var.system_disk_size

  # 分配公网 IP（按固定带宽计费）
  internet_charge_type       = "PayByBandwidth"
  internet_max_bandwidth_out = var.internet_bandwidth

  # 首次启动自动部署
  user_data = base64encode(templatefile("${path.module}/cloud-init.yaml.tpl", {
    repo_url      = var.repo_url
    repo_branch   = var.repo_branch
    embed_api_key = var.embed_api_key
    site_address  = var.site_address
  }))
}
