output "repository_url" {
  description = "URL used to tag and push release images."
  value       = aws_ecr_repository.app.repository_url
}
