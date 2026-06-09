variable "access_key" {
  description = "阿里云 AccessKey ID"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "阿里云 AccessKey Secret"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "地域。香港免备案：cn-hongkong"
  type        = string
  default     = "cn-hongkong"
}

variable "instance_type" {
  description = "ECS 规格。2核4G 经济型，几百人足够"
  type        = string
  default     = "ecs.e-c1m2.large"
}

variable "instance_password" {
  description = "ECS root 密码（也可改用 key_name 走密钥登录）"
  type        = string
  sensitive   = true
}

variable "system_disk_size" {
  description = "系统盘大小 GB"
  type        = number
  default     = 40
}

variable "internet_bandwidth" {
  description = "公网出带宽峰值上限 Mbps（按流量计费，仅封顶不固定收费；突发访问更顺）"
  type        = number
  default     = 100
}

# --- 应用层参数（注入 cloud-init）---

variable "repo_url" {
  description = "项目 git 仓库地址，cloud-init 会 clone"
  type        = string
}

variable "repo_branch" {
  description = "部署分支"
  type        = string
  default     = "main"
}

variable "embed_api_key" {
  description = "SiliconFlow API key（写入服务器 .env，不进 git）"
  type        = string
  sensitive   = true
}

variable "site_address" {
  description = "Caddy 站点地址。填域名(自动HTTPS)或 :80(无域名按IP访问)"
  type        = string
  default     = ":80"
}

variable "ssh_cidr" {
  description = "允许 SSH(22) 访问的来源网段。建议收紧为你的公网 IP/32"
  type        = string
  default     = "0.0.0.0/0"
}
