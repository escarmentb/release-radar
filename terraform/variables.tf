variable "aws_region" {
  description = "AWS region for the image repository."
  type        = string
  default     = "us-east-1"
}

variable "repository_name" {
  description = "Name of the ECR repository."
  type        = string
  default     = "release-radar"
}
