variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "translate-doc"
}

variable "cognito_domain_prefix" {
  description = "Cognito domain prefix"
  type        = string
  default     = "translate-doc"
}

variable "allowed_origins" {
  description = "Allowed origins for CORS"
  type        = list(string)
  default     = ["http://localhost:5173", "http://localhost:3000"]
}