Grafana Argo CD Application

This folder contains an Argo CD Application manifest that will deploy Grafana and any related monitoring resources stored under `k8s/grafana` in this repository.

How it works

- The Application `grafana-monitoring` points at this repository and the `k8s/grafana` path.
- It is configured to create the `monitoring` namespace automatically and will recurse into subdirectories when syncing.

Assumptions

- Repository URL: https://github.com/AthipornP/sample-docker-image.git
- Branch: `main`
- Argo CD is installed in the `argocd` namespace and the Argo CD CRD `Application` is available.

To apply

1. kubectl apply -f k8s/grafana/argocd-application.yaml

Or using the argocd CLI:

1. argocd app create -f k8s/grafana/argocd-application.yaml

Notes

- Place your Grafana Deployment/Service/ConfigMap/Ingress/Prometheus scrape configs under `k8s/grafana` so Argo CD will manage them.
- If you want a different repo URL or branch, edit `spec.source` in the Application manifest.
