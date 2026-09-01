# Container Security

The runtime image is configured for a narrow execution profile:

- Run as a non-root user.
- Drop Linux capabilities.
- Use a read-only filesystem.
- Disable privilege escalation.
- Keep dependencies minimal.

Review these controls whenever changing the Dockerfile or Kubernetes security context.
