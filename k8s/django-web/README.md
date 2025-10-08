Postgres StatefulSet backed by Ceph (rook-ceph-block)

This folder now contains a headless Service and a StatefulSet for Postgres that
uses `storageClassName: rook-ceph-block` via `volumeClaimTemplates`.

Requirements
- A Ceph/Rook storageClass named `rook-ceph-block` must exist in the cluster.
  If you don't have Rook/Ceph installed, follow the Rook quickstart for your
  Kubernetes version: https://rook.io/docs/rook/v1.12/ceph-quickstart.html

How to apply
- With kubectl:
  kubectl apply -k k8s/django-web

Notes
- The StatefulSet replica is set to 1. For HA you should configure Postgres
  replication (primary/replica) or use a Postgres operator.
- This manifest does NOT configure TLS between clients and Postgres. If you're
  exposing Postgres externally (NodePort) take extra care (VPN / firewalls /
  TLS / auth).
