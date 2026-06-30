terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags { tags = { Project = "release-radar", ManagedBy = "terraform" } }
}

resource "aws_ecr_repository" "app" {
  name                 = var.repository_name
  image_tag_mutability = "IMMUTABLE"
  force_delete         = false
  encryption_configuration { encryption_type = "AES256" }
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name
  policy = jsonencode({ rules = [{
    rulePriority = 1
    description  = "Retain the newest 30 release images"
    selection = {
      tagStatus   = "any"
      countType   = "imageCountMoreThan"
      countNumber = 30
    }
    action = { type = "expire" }
  }] })
}
