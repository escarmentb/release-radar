# Terraform Notes

The Terraform module manages the optional ECR repository used for release images.

Before applying:

- Run `terraform fmt -check -recursive terraform`.
- Review the selected repository name and tags.
- Confirm image scanning and encryption remain enabled.
- Use `terraform plan` before `terraform apply`.

Destroy the repository only after removing images that must not be retained.
