This folder contains Kubernetes manifests (suitable for Argo CD) for the sample projects in this repository.

Structure:
-- namespace.yaml  -> creates namespace `customer-portal`
- svelte-portal/  -> Deployment, Service (NodePort 23000), ConfigMap, Secret
- django-web/     -> Deployment, Service (NodePort 23001), Postgres deployment, ConfigMap, Secret
- php-web/        -> Deployment, Service (NodePort 23002), ConfigMap

Notes:
- All Services are NodePort and use ports in the requested 23000+ range.
-- All Deployments are in namespace `customer-portal`.
- Environment variables are provided via ConfigMaps and Secrets. Fill secrets before applying.
- Volume mounts: Django deployment mounts `/app` from an ephemeral `emptyDir` to reflect the docker-compose bind-mount used during development; for production replace with a proper PVC and copy application code into image.

Apply locally with kubectl:

  kubectl apply -f namespace.yaml
  kubectl apply -f svelte-portal/ -n customer-portal
  kubectl apply -f django-web/ -n customer-portal
  kubectl apply -f php-web/ -n customer-portal

Argo CD
------
Below is a minimal Argo CD Application example (copy and adapt per project):

apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: svelte-portal
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/your-org/sample-docker-image'
    targetRevision: HEAD
    path: k8s/svelte-portal
  destination:
    server: 'https://kubernetes.default.svc'
  namespace: customer-portal
  syncPolicy:
    automated: {}

Create a similar Application resource per project (change path and name).
