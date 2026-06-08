output "public_ip" {
  description = "ECS 公网 IP"
  value       = alicloud_instance.main.public_ip
}

output "ssh_command" {
  description = "SSH 登录命令"
  value       = "ssh root@${alicloud_instance.main.public_ip}"
}

output "site_url" {
  description = "访问地址"
  value       = var.site_address == ":80" ? "http://${alicloud_instance.main.public_ip}" : "https://${trimprefix(var.site_address, ":")}"
}
