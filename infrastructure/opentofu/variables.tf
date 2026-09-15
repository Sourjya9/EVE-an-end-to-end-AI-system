variable "aws_region" {
  description = "AWS region for resource provisioning"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_username" {
  description = "Master database username"
  type        = string
  default     = "eve_admin"
}

variable "db_password" {
  description = "Master database password"
  type        = string
  sensitive   = true
}

variable "groq_api_key" {
  description = "Groq Cloud inference API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "jina_api_key" {
  description = "Jina AI embeddings API key"
  type        = string
  sensitive   = true
  default     = ""
}
