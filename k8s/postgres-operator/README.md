# CloudNativePG PostgreSQL Operator Setup

This folder contains manifests for deploying CloudNativePG operator and a PostgreSQL High Availability cluster.

## What This Provides

- **Automatic Failover**: If primary fails, operator promotes a replica to primary
- **Streaming Replication**: Data is continuously replicated to standby instances  
- **Zero-Downtime Maintenance**: Operator handles rolling updates without service interruption
- **Backup/Restore**: Built-in support for pg_basebackup and WAL archiving
- **Connection Pooling**: Optional PgBouncer integration
- **Monitoring**: Prometheus metrics and PostgreSQL logs

## Architecture

- **django-postgres-cluster**: 3-instance cluster (1 primary + 2 replicas)
- **django-postgres**: Service pointing to current primary (read/write)
- **django-postgres-ro**: Service pointing to replicas (read-only queries)
- **Storage**: Each instance gets its own PVC backed by Ceph (rook-ceph-block)

## Installation Steps

1. **Install the operator** (applies CRDs and controller):
   ```bash
   kubectl apply -f cloudnativepg-operator.yaml
   ```

2. **Wait for operator to be ready**:
   ```bash
   kubectl -n cloudnativepg-system get pods
   kubectl -n cloudnativepg-system logs deployment/cloudnativepg-controller-manager
   ```

3. **Deploy the PostgreSQL cluster**:
   ```bash
   kubectl apply -f django-postgres-cluster.yaml
   ```

4. **Monitor cluster bootstrap**:
   ```bash
   kubectl -n customer-portal get clusters
   kubectl -n customer-portal get pods -l postgresql=django-postgres-cluster
   kubectl -n customer-portal logs django-postgres-cluster-1 -f
   ```

## Verification Commands

- **Check cluster status**:
  ```bash
  kubectl -n customer-portal get clusters django-postgres-cluster -o yaml
  ```

- **Check services**:
  ```bash
  kubectl -n customer-portal get svc -l app=django-postgres-cluster
  ```

- **Test failover** (carefully):
  ```bash
  # Delete primary pod - operator should promote replica
  kubectl -n customer-portal delete pod django-postgres-cluster-1
  ```

## Configuration

- **Instances**: 3 (configurable in spec.instances)
- **Storage**: 10Gi per instance via Ceph PVC
- **Resources**: 256Mi RAM, 100m CPU request per instance
- **Database**: `django` owned by user `django`
- **Credentials**: Stored in Secret `django-postgres-credentials`

## Migration from StatefulSet

The old StatefulSet-based Postgres is commented out in kustomization.yaml.
To migrate data:

1. Take a dump from old cluster:
   ```bash
   kubectl -n customer-portal exec django-postgres-0 -- pg_dump -U django django > backup.sql
   ```

2. Restore to new cluster:
   ```bash
   kubectl -n customer-portal exec django-postgres-cluster-1 -- psql -U django django < backup.sql
   ```

## Troubleshooting

- **Operator logs**: `kubectl -n cloudnativepg-system logs deployment/cloudnativepg-controller-manager`
- **Cluster events**: `kubectl -n customer-portal describe cluster django-postgres-cluster`
- **Pod logs**: `kubectl -n customer-portal logs django-postgres-cluster-1`
- **Cluster status**: `kubectl cnpg status django-postgres-cluster` (requires cnpg CLI)

## Production Considerations

- Configure backup to S3/object storage
- Set up monitoring with Prometheus
- Tune PostgreSQL parameters for your workload
- Consider using PgBouncer for connection pooling
- Set appropriate resource requests/limits
- Configure pod anti-affinity to spread instances across nodes