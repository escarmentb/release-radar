# Kubernetes Operations

Operational checks before production rollout:

- Render manifests with `kubectl kustomize k8s/overlays/prod`.
- Confirm the deployment image tag is immutable.
- Confirm resource requests and limits fit the target cluster.
- Verify the PodDisruptionBudget preserves at least one available replica.
- Confirm the NetworkPolicy matches the namespace traffic model.
