# SigNoz Observability Platform

SigNoz เป็น Open-source Observability Platform สำหรับ monitoring, tracing และ logging แบบครบวงจร

## Components

### 1. ClickHouse
- **หน้าที่**: Time-series database เก็บ traces, metrics, logs
- **Ports**: 9000 (Native), 8123 (HTTP)
- **Storage**: 20Gi PVC บน rook-ceph-block

### 2. Query Service (signoz-0)
- **หน้าที่**: Backend API สำหรับ query และ aggregate data จาก ClickHouse
- **Ports**: 8080 (HTTP), 8085 (Internal), 4320 (OpAMP)
- **UI**: Dashboard, Traces, Metrics, Logs visualization

### 3. Frontend (signoz service)
- **หน้าที่**: Web UI สำหรับผู้ใช้
- **NodePort**: 30301 (เข้าถึงจากภายนอก cluster)

### 4. OTEL Collector
- **หน้าที่**: รับและประมวลผล telemetry data จาก applications
- **Ports**: 
  - 4317 (OTLP gRPC)
  - 4318 (OTLP HTTP)
  - 14250 (Jaeger gRPC)
  - 14268 (Jaeger HTTP)
  - 8081, 8082 (Logs)

### 5. ZooKeeper
- **หน้าที่**: Coordination service สำหรับ ClickHouse cluster
- **Ports**: 2181 (Client), 2888, 3888 (Cluster)
- **Storage**: 8Gi PVC บน rook-ceph-block

### 6. ClickHouse Operator
- **หน้าที่**: จัดการ ClickHouse lifecycle, scaling, backup
- **Port**: 8888 (Metrics)

### 7. Schema Migrator
- **หน้าที่**: สร้าง/อัพเดท database schemas
- **Type**: Kubernetes Job (รันครั้งเดียว)

## การ Deploy

### 1. สร้าง RBAC สำหรับ ClickHouse Operator

```bash
kubectl apply -f clickhouse-operator-rbac.yaml
```

### 2. Deploy ผ่าน Argo CD

```bash
kubectl apply -f argocd-application.yaml
```

### 3. สร้าง Service (ถ้า Argo ไม่สร้างอัตโนมัติ)

```bash
kubectl apply -f signoz-service.yaml
```

### 4. ตรวจสอบสถานะ

```bash
# ดู pods
kubectl get pods -n signoz

# ดู services
kubectl get svc -n signoz

# ดู Argo Application
kubectl get application signoz -n argocd
```

## เข้าถึง SigNoz UI

**URL**: `http://<node-ip>:30301`

ตัวอย่าง:
```bash
# ดู Node IP
kubectl get nodes -o wide

# เข้าถึง UI
http://10.191.10.61:30301
```

## การส่งข้อมูล Telemetry

### OpenTelemetry (แนะนำ)

```yaml
# OTLP gRPC
endpoint: signoz-otel-collector.signoz.svc.cluster.local:4317

# OTLP HTTP
endpoint: http://signoz-otel-collector.signoz.svc.cluster.local:4318
```

### Jaeger

```yaml
# Jaeger gRPC
endpoint: signoz-otel-collector.signoz.svc.cluster.local:14250

# Jaeger HTTP
endpoint: http://signoz-otel-collector.signoz.svc.cluster.local:14268
```

### Logs

```yaml
# Heroku style logs
endpoint: http://signoz-otel-collector.signoz.svc.cluster.local:8081

# JSON logs
endpoint: http://signoz-otel-collector.signoz.svc.cluster.local:8082
```

## Configuration

Configuration อยู่ใน `argocd-application.yaml` ภายใต้ `spec.source.helm.values`

### Storage Class

ใช้ `rook-ceph-block` สำหรับ PVC ทั้งหมด:
- ClickHouse: 20Gi
- ZooKeeper: 8Gi (default)

### ปรับ Resource Limits

```yaml
queryService:
  resources:
    limits:
      memory: "2Gi"
      cpu: "1000m"
```

### เปลี่ยน Storage Size

```yaml
clickhouse:
  persistence:
    size: 50Gi
```

### เปลี่ยน Service Type

```yaml
frontend:
  service:
    type: LoadBalancer  # หรือ ClusterIP
```

## การตรวจสอบสถานะ

```bash
# ดู pods ทั้งหมด
kubectl get pods -n signoz

# ดู services
kubectl get svc -n signoz

# ดู logs
kubectl logs -n signoz -l app.kubernetes.io/component=otel-collector -f
kubectl logs -n signoz -l app.kubernetes.io/component=query-service -f
```

## Troubleshooting

### Pod ไม่ start

```bash
kubectl describe pod -n signoz <pod-name>
kubectl logs -n signoz <pod-name>
```

### ClickHouse ไม่สามารถ mount volume ได้

```bash
# ตรวจสอบ PVC
kubectl get pvc -n signoz
kubectl describe pvc -n signoz

# ตรวจสอบ StorageClass
kubectl get storageclass
```

### OTEL Collector ไม่รับ data

```bash
# ตรวจสอบ service endpoint
kubectl get ep -n signoz

# ทดสอบ connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  wget -O- http://signoz-otel-collector.signoz.svc.cluster.local:4318/v1/traces
```

### Argo CD Sync ล้มเหลว

```bash
# ดู sync status
argocd app get signoz

# Sync แบบบังคับ
argocd app sync signoz --force

# ดู Argo logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller
```

## การลบ Deployment

```bash
# ลบด้วย Argo CD
kubectl delete application signoz -n argocd

# หรือลบ namespace ทั้งหมด
kubectl delete namespace signoz
```

## Files

```
signoz/
├── README.md                          # เอกสารนี้
├── argocd-application.yaml            # Argo CD Application (Helm chart v0.99.0)
├── clickhouse-operator-rbac.yaml      # RBAC สำหรับ ClickHouse Operator
└── signoz-service.yaml                # Service สำหรับ Frontend UI (NodePort 30301)
```

## References

- [SigNoz Official Docs](https://signoz.io/docs/)
- [SigNoz Helm Chart](https://github.com/SigNoz/charts)
- [OpenTelemetry](https://opentelemetry.io/)
- [ClickHouse](https://clickhouse.com/)

```

SigNoz Platform- **Traces** - Distributed tracing

├── Query Service (signoz-0)         - Web UI และ Query API

├── OTEL Collector                   - รับ telemetry data (traces, metrics, logs)```- **Metrics** - Application และ infrastructure metrics

├── ClickHouse                       - Time-series database

├── ZooKeeper                        - Coordination service สำหรับ ClickHouseSigNoz Platform- **Logs** - Centralized logging

└── Schema Migrator                  - Database migration jobs

```├── Query Service (signoz-0)         - Web UI และ Query API



## Services และหน้าที่├── OTEL Collector                   - รับ telemetry data (traces, metrics, logs)## Components



### 1. Query Service (signoz-0)├── ClickHouse                       - Time-series database

- **Port**: 8080 (HTTP), 8085 (Internal), 4320 (OpAMP)

- **NodePort**: 30301 (เข้าถึง UI)├── ZooKeeper                        - Coordination service สำหรับ ClickHouse1. **ClickHouse** - Time-series database สำหรับเก็บ telemetry data

- **หน้าที่**:

  - Web UI สำหรับ Dashboard, Traces, Metrics, Logs└── Schema Migrator                  - Database migration jobs2. **Query Service** - API backend สำหรับ query ข้อมูล

  - Query API สำหรับดึงข้อมูลจาก ClickHouse

  - Alert Manager```3. **Frontend** - Web UI สำหรับ visualization



### 2. OTEL Collector4. **OTEL Collector** - รับ telemetry data จาก applications

- **Ports**: 4317 (gRPC), 4318 (HTTP), 14250 (Jaeger gRPC), 14268 (Jaeger HTTP), 8081-8082 (Logs)

- **หน้าที่**:## Services และหน้าที่

  - รับ telemetry data จาก applications (OpenTelemetry, Jaeger, Zipkin)

  - Process และ transform data## การ Deploy ด้วย Argo CD + Helm Chart

  - ส่งข้อมูลไปเก็บใน ClickHouse

### 1. **Query Service (signoz-0)**

### 3. ClickHouse (chi-signoz-clickhouse-cluster-0-0-0)

- **Ports**: 9000 (Native), 8123 (HTTP), 9009 (Interserver)- **Port**: 8080 (HTTP), 8085 (Internal), 4320 (OpAMP)Deployment นี้ใช้ **SigNoz Official Helm Chart** ผ่าน Argo CD

- **หน้าที่**:

  - เก็บ traces, metrics, logs ในรูปแบบ columnar database- **NodePort**: 30301 (เข้าถึง UI)

  - รองรับ high-performance queries

  - มี PVC 20Gi บน rook-ceph-block- **หน้าที่**: ### ติดตั้งด้วย Argo CD



### 4. ZooKeeper (signoz-zookeeper-0)  - Web UI สำหรับ Dashboard, Traces, Metrics, Logs

- **Ports**: 2181 (Client), 2888 (Follower), 3888 (Election)

- **หน้าที่**:  - Query API สำหรับดึงข้อมูลจาก ClickHouse```bash

  - Coordination service สำหรับ ClickHouse cluster

  - Manage cluster metadata และ configuration  - Alert Manager# Apply Argo Application

  - มี PVC 8Gi บน rook-ceph-block

kubectl apply -f argocd-application.yaml

### 5. ClickHouse Operator

- **Port**: 8888 (Metrics)### 2. **OTEL Collector**

- **หน้าที่**:

  - จัดการ ClickHouse cluster lifecycle- **Ports**: 4317 (gRPC), 4318 (HTTP), 14250 (Jaeger gRPC), 14268 (Jaeger HTTP), 8081-8082 (Logs)# ดูสถานะ

  - Handle configuration changes

  - Auto-scaling และ backup- **หน้าที่**:kubectl get application signoz -n argocd



### 6. Schema Migrator (Jobs)  - รับ telemetry data จาก applications (OpenTelemetry, Jaeger, Zipkin)kubectl get pods -n signoz

- **Types**: sync-init, async-init

- **หน้าที่**:  - Process และ transform data

  - สร้าง database schemas (traces, metrics, logs)

  - Migrate schema เมื่อ upgrade version  - ส่งข้อมูลไปเก็บใน ClickHouse# Sync (ถ้า auto-sync ไม่ทำงาน)

  - รันครั้งเดียวแล้วเสร็จ (Job Completed)

argocd app sync signoz

## การติดตั้ง

### 3. **ClickHouse (chi-signoz-clickhouse-cluster-0-0-0)**```

### 1. สร้าง RBAC สำหรับ ClickHouse Operator

- **Ports**: 9000 (Native), 8123 (HTTP), 9009 (Interserver)

```bash

kubectl apply -f clickhouse-operator-rbac.yaml- **หน้าที่**:### หรือติดตั้งด้วย Helm โดยตรง

```

  - เก็บ traces, metrics, logs ในรูปแบบ columnar database

### 2. Deploy SigNoz ผ่าน Argo CD

  - รองรับ high-performance queries```bash

```bash

kubectl apply -f argocd-application.yaml  - มี PVC 20Gi บน rook-ceph-block# เพิ่ม Helm repository

```

helm repo add signoz https://charts.signoz.io

### 3. ตรวจสอบสถานะ

### 4. **ZooKeeper (signoz-zookeeper-0)**helm repo update

```bash

# ดู pods- **Ports**: 2181 (Client), 2888 (Follower), 3888 (Election)

kubectl get pods -n signoz

- **หน้าที่**:# ติดตั้ง SigNoz

# ดู services

kubectl get svc -n signoz  - Coordination service สำหรับ ClickHouse clusterhelm install signoz signoz/signoz \



# ดู Argo Application  - Manage cluster metadata และ configuration  --namespace signoz \

kubectl get application signoz -n argocd

```  - มี PVC 8Gi บน rook-ceph-block  --create-namespace \



## การเข้าถึง SigNoz UI  -f argocd-application.yaml



### ผ่าน NodePort (Default)### 5. **ClickHouse Operator**



```bash- **Port**: 8888 (Metrics)# Upgrade

# เข้าถึงผ่าน NodePort 30301

http://<NODE_IP>:30301- **หน้าที่**:helm upgrade signoz signoz/signoz \



# ตัวอย่าง  - จัดการ ClickHouse cluster lifecycle  --namespace signoz \

http://10.191.10.61:30301

```  - Handle configuration changes  -f argocd-application.yaml



### ผ่าน Port Forward  - Auto-scaling และ backup```



```bash

kubectl port-forward -n signoz svc/signoz 3301:8080

# เข้าถึงที่ http://localhost:3301### 6. **Schema Migrator (Jobs)**## การเข้าถึง SigNoz UI

```

- **Types**: sync-init, async-init

## การส่ง Telemetry Data ไปยัง SigNoz

- **หน้าที่**:### ผ่าน NodePort (Default)

### OTLP Endpoints

  - สร้าง database schemas (traces, metrics, logs)

```

# OTLP gRPC  - Migrate schema เมื่อ upgrade version```bash

http://signoz-otel-collector.signoz.svc.cluster.local:4317

  - รันครั้งเดียวแล้วเสร็จ (Job Completed)# เข้าถึงผ่าน NodePort 30301

# OTLP HTTP

http://signoz-otel-collector.signoz.svc.cluster.local:4318http://<NODE_IP>:30301

```

## การ Deploy```

### ตัวอย่าง: Python (OpenTelemetry)



```python

from opentelemetry import trace### 1. สร้าง RBAC สำหรับ ClickHouse Operator### ผ่าน Port Forward

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk.trace import TracerProvider```bash

from opentelemetry.sdk.trace.export import BatchSpanProcessor

kubectl apply -f clickhouse-operator-rbac.yaml```bash

trace.set_tracer_provider(TracerProvider())

otlp_exporter = OTLPSpanExporter(```kubectl port-forward -n signoz svc/signoz-frontend 3301:3301

    endpoint="http://signoz-otel-collector.signoz.svc.cluster.local:4317",

    insecure=True# เข้าถึงที่ http://localhost:3301

)

trace.get_tracer_provider().add_span_processor(### 2. Deploy SigNoz ผ่าน Argo CD```

    BatchSpanProcessor(otlp_exporter)

)```bash

```

kubectl apply -f argocd-application.yaml## การส่ง Telemetry Data ไปยัง SigNoz

### ตัวอย่าง: Node.js (OpenTelemetry)

```

```javascript

const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');### OTLP gRPC Endpoint

const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');

### 3. สร้าง Service สำหรับ Frontend (ถ้า Argo ไม่สร้างอัตโนมัติ)```

const provider = new NodeTracerProvider();

const exporter = new OTLPTraceExporter({```bashhttp://signoz-otel-collector.signoz.svc.cluster.local:4317

  url: 'http://signoz-otel-collector.signoz.svc.cluster.local:4317'

});kubectl apply -f signoz-service.yaml```

provider.addSpanProcessor(new BatchSpanProcessor(exporter));

provider.register();```

```

### OTLP HTTP Endpoint

## Configuration

### 4. ตรวจสอบสถานะ```

Configuration อยู่ใน `argocd-application.yaml` ภายใต้ `spec.source.helm.values`

```bashhttp://signoz-otel-collector.signoz.svc.cluster.local:4318

### ปรับ Resource Limits

# ดู pods```

```yaml

queryService:kubectl get pods -n signoz

  resources:

    limits:### ตัวอย่างการ Config ใน Application

      memory: "2Gi"

      cpu: "1000m"# ดู services

```

kubectl get svc -n signoz**Python (OpenTelemetry)**

### เปลี่ยน Storage Size

```python

```yaml

clickhouse:# ดู Argo Applicationfrom opentelemetry import trace

  persistence:

    size: 50Gikubectl get application signoz -n argocdfrom opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

```

```from opentelemetry.sdk.trace import TracerProvider

### เปลี่ยน Service Type

from opentelemetry.sdk.trace.export import BatchSpanProcessor

```yaml

signoz:## เข้าถึง SigNoz UI

  service:

    type: LoadBalancer  # หรือ ClusterIPtrace.set_tracer_provider(TracerProvider())

```

**URL**: `http://<node-ip>:30301`otlp_exporter = OTLPSpanExporter(

## การตรวจสอบสถานะ

    endpoint="http://signoz-otel-collector.signoz.svc.cluster.local:4317",

```bash

# ดู pods ทั้งหมดตัวอย่าง:    insecure=True

kubectl get pods -n signoz

```bash)

# ดู services

kubectl get svc -n signoz# ดู Node IPtrace.get_tracer_provider().add_span_processor(



# ดู Argo CD Applicationkubectl get nodes -o wide    BatchSpanProcessor(otlp_exporter)

kubectl get application signoz -n argocd -o yaml

)

# ดู logs

kubectl logs -n signoz -l app.kubernetes.io/component=otel-collector -f# เข้าถึง UI```

kubectl logs -n signoz -l app.kubernetes.io/name=signoz -f

```http://10.191.10.61:30301



## Troubleshooting```**Node.js (OpenTelemetry)**



### Pod ไม่ start```javascript



```bash## การส่งข้อมูล Telemetryconst { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');

kubectl describe pod -n signoz <pod-name>

kubectl logs -n signoz <pod-name>const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');

```

### OpenTelemetry (แนะนำ)

### ClickHouse ไม่สามารถ mount volume ได้

```yamlconst provider = new NodeTracerProvider();

```bash

# ตรวจสอบ PVC# OTLP gRPCconst exporter = new OTLPTraceExporter({

kubectl get pvc -n signoz

kubectl describe pvc -n signozendpoint: signoz-otel-collector.signoz.svc.cluster.local:4317  url: 'http://signoz-otel-collector.signoz.svc.cluster.local:4317'



# ตรวจสอบ StorageClass});

kubectl get storageclass

```# OTLP HTTPprovider.addSpanProcessor(new BatchSpanProcessor(exporter));



### OTEL Collector ไม่รับ dataendpoint: http://signoz-otel-collector.signoz.svc.cluster.local:4318provider.register();



```bash``````

# ตรวจสอบ service endpoint

kubectl get ep -n signoz



# ทดสอบ connectivity### Jaeger## การตรวจสอบสถานะ

kubectl run -it --rm debug --image=busybox --restart=Never -- \

  wget -O- http://signoz-otel-collector.signoz.svc.cluster.local:4318/v1/traces```yaml

```

# Jaeger gRPC```bash

### Argo CD Sync ล้มเหลว

endpoint: signoz-otel-collector.signoz.svc.cluster.local:14250# ดู pods ทั้งหมด

```bash

# ดู sync statuskubectl get pods -n signoz

argocd app get signoz

# Jaeger HTTP

# Sync แบบบังคับ

argocd app sync signoz --forceendpoint: http://signoz-otel-collector.signoz.svc.cluster.local:14268# ดู services



# ดู Argo logs```kubectl get svc -n signoz

kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller

```



## การลบ Deployment### Logs# ดู Argo CD Application



```bash```yamlkubectl get application signoz -n argocd -o yaml

# ลบด้วย Argo CD

kubectl delete application signoz -n argocd# Heroku style logs



# หรือลบ namespace ทั้งหมดendpoint: http://signoz-otel-collector.signoz.svc.cluster.local:8081# ดู logs

kubectl delete namespace signoz

```kubectl logs -n signoz -l app.kubernetes.io/component=otel-collector -f



## Files# JSON logskubectl logs -n signoz -l app.kubernetes.io/component=query-service -f



```endpoint: http://signoz-otel-collector.signoz.svc.cluster.local:8082```

signoz/

├── README.md                          # เอกสารนี้```

├── argocd-application.yaml            # Argo CD Application (Helm chart v0.99.0)

├── clickhouse-operator-rbac.yaml      # RBAC สำหรับ ClickHouse Operator## Configuration

└── signoz-service.yaml                # Service สำหรับ Frontend UI (NodePort 30301)

```## Configuration



## References### Helm Values



- [SigNoz Official Docs](https://signoz.io/docs/)### Storage Class

- [SigNoz Helm Chart](https://github.com/SigNoz/charts)

- [OpenTelemetry](https://opentelemetry.io/)ใช้ `rook-ceph-block` สำหรับ PVC ทั้งหมด:Configuration อยู่ใน `argocd-application.yaml` ภายใต้ `spec.source.helm.values`

- [ClickHouse](https://clickhouse.com/)

- ClickHouse: 20Gi

- ZooKeeper: 8Gi (default)#### ปรับ Resource Limits



### Resources```yaml

- **ClickHouse**: 1Gi-2Gi RAM, 500m-1000m CPUqueryService:

- **Query Service**: 512Mi-1Gi RAM, 200m-500m CPU  resources:

- **OTEL Collector**: 512Mi-1Gi RAM, 200m-500m CPU    limits:

- **ZooKeeper**: 256Mi-512Mi RAM, 100m-250m CPU      memory: "2Gi"

      cpu: "1000m"

## Troubleshooting```



### Pods ไม่ Running#### เปลี่ยน Storage Size

```bash

# ดู logs```yaml

kubectl logs <pod-name> -n signozclickhouse:

  persistence:

# ดู events    size: 50Gi

kubectl describe pod <pod-name> -n signoz```

```

#### เปลี่ยน Service Type

### ClickHouse ไม่เชื่อมต่อ ZooKeeper

```bash```yaml

# ตรวจสอบ ZooKeeperfrontend:

kubectl logs signoz-zookeeper-0 -n signoz  service:

    type: LoadBalancer  # หรือ ClusterIP

# ตรวจสอบ network```

kubectl exec -it signoz-zookeeper-0 -n signoz -- nc -zv signoz-zookeeper 2181

```## Troubleshooting



### Service ไม่สร้าง### Pod ไม่ start

```bash```bash

# ลบแล้วให้ Argo สร้างใหม่kubectl describe pod -n signoz <pod-name>

kubectl delete svc signoz -n signozkubectl logs -n signoz <pod-name>

```

# หรือสร้างด้วยตนเอง

kubectl apply -f signoz-service.yaml### ClickHouse ไม่สามารถ mount volume ได้

``````bash

# ตรวจสอบ PVC

### Argo Application OutOfSynckubectl get pvc -n signoz

```bashkubectl describe pvc -n signoz

# Force sync

kubectl -n argocd patch application signoz --type json -p='[{"op": "replace", "path": "/operation", "value": {"sync": {"revision": "0.99.0"}}}]'# ตรวจสอบ StorageClass

```kubectl get storageclass

```

## Files

### OTEL Collector ไม่รับ data

``````bash

signoz/# ตรวจสอบ service endpoint

├── README.md                          # เอกสารนี้kubectl get ep -n signoz

├── argocd-application.yaml            # Argo CD Application (Helm chart v0.99.0)

├── clickhouse-operator-rbac.yaml      # RBAC สำหรับ ClickHouse Operator# ทดสอบ connectivity

└── signoz-service.yaml                # Service สำหรับ Frontend UI (NodePort 30301)kubectl run -it --rm debug --image=busybox --restart=Never -- \

```  wget -O- http://signoz-otel-collector.signoz.svc.cluster.local:4318/v1/traces

```

## References

### Argo CD Sync ล้มเหลว

- [SigNoz Official Docs](https://signoz.io/docs/)```bash

- [SigNoz Helm Chart](https://github.com/SigNoz/charts)# ดู sync status

- [OpenTelemetry](https://opentelemetry.io/)argocd app get signoz

- [ClickHouse](https://clickhouse.com/)

# Sync แบบบังคับ
argocd app sync signoz --force

# ดู Argo logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller
```

## การลบ Deployment

```bash
# ลบด้วย Argo CD
kubectl delete application signoz -n argocd

# หรือลบ namespace ทั้งหมด
kubectl delete namespace signoz
```

## หมายเหตุ

- SigNoz Frontend เปิดให้เข้าถึงผ่าน NodePort 30301
- ClickHouse ใช้ Rook-Ceph สำหรับ persistent storage
- Helm Chart จาก SigNoz official repository: https://charts.signoz.io
- Documentation: https://signoz.io/docs/install/kubernetes/
- Chart Version: 0.54.2 (ตรวจสอบ version ล่าสุดได้ที่ https://github.com/SigNoz/charts)

## Manual Deployment Files (เก่า - ไม่ใช้แล้ว)

ไฟล์เหล่านี้เก็บไว้เป็น reference เท่านั้น:
- `namespace.yaml`
- `clickhouse-deployment.yaml`
- `deployment.yaml`
- `service.yaml`
- `kustomization.yaml`

**ใช้ `argocd-application.yaml` แทน**

### 1. สร้าง Application ใน Argo CD UI

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: signoz
  namespace: argocd
spec:
  project: default
  source:
    repoURL: <YOUR_GIT_REPO_URL>
    targetRevision: HEAD
    path: k8s/signoz
  destination:
    server: https://kubernetes.default.svc
    namespace: signoz
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### 2. หรือใช้ kubectl apply

```bash
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: signoz
  namespace: argocd
spec:
  project: default
  source:
    repoURL: <YOUR_GIT_REPO_URL>
    targetRevision: HEAD
    path: k8s/signoz
  destination:
    server: https://kubernetes.default.svc
    namespace: signoz
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
EOF
```

### 3. Manual Deploy (ทดสอบก่อน)

```bash
# Deploy ด้วย kubectl
kubectl apply -k /home/cbe/sample-docker-image/k8s/signoz

# ตรวจสอบ deployment
kubectl get pods -n signoz
kubectl get svc -n signoz
```

## การเข้าถึง SigNoz UI

### ผ่าน NodePort (Default)

```bash
# เข้าถึงผ่าน NodePort 30301
http://<NODE_IP>:30301
```

### ผ่าน Port Forward

```bash
kubectl port-forward -n signoz svc/signoz-frontend 3301:3301
# เข้าถึงที่ http://localhost:3301
```

## การส่ง Telemetry Data ไปยัง SigNoz

### OTLP gRPC Endpoint
```
http://signoz-otel-collector.signoz.svc.cluster.local:4317
```

### OTLP HTTP Endpoint
```
http://signoz-otel-collector.signoz.svc.cluster.local:4318
```

### ตัวอย่างการ Config ใน Application

**Python (OpenTelemetry)**
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(
    endpoint="http://signoz-otel-collector.signoz.svc.cluster.local:4317",
    insecure=True
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
```

**Node.js (OpenTelemetry)**
```javascript
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');

const provider = new NodeTracerProvider();
const exporter = new OTLPTraceExporter({
  url: 'http://signoz-otel-collector.signoz.svc.cluster.local:4317'
});
provider.addSpanProcessor(new BatchSpanProcessor(exporter));
provider.register();
```

## การตรวจสอบสถานะ

```bash
# ดู pods ทั้งหมด
kubectl get pods -n signoz

# ดู services
kubectl get svc -n signoz

# ดู logs
kubectl logs -n signoz -l app=signoz -f

# ดู ClickHouse logs
kubectl logs -n signoz -l component=clickhouse -f

# ดู Query Service logs
kubectl logs -n signoz -l component=query-service -f
```

## Storage Configuration

ClickHouse ใช้ PersistentVolumeClaim ขนาด 10Gi 

หากต้องการเปลี่ยนขนาด แก้ไขที่:
```yaml
# ใน clickhouse-deployment.yaml
volumeClaimTemplates:
  - metadata:
      name: clickhouse-data
    spec:
      resources:
        requests:
          storage: 10Gi  # <-- เปลี่ยนตรงนี้
```

## Resource Limits

แต่ละ component มี resource requests/limits ดังนี้:

- **ClickHouse**: 512Mi-1Gi RAM, 200m-1000m CPU
- **Query Service**: 256Mi-512Mi RAM, 100m-500m CPU
- **Frontend**: 128Mi-256Mi RAM, 50m-200m CPU
- **OTEL Collector**: 256Mi-512Mi RAM, 100m-500m CPU

## Troubleshooting

### Pod ไม่ start
```bash
kubectl describe pod -n signoz <pod-name>
kubectl logs -n signoz <pod-name>
```

### ClickHouse ไม่สามารถ mount volume ได้
```bash
# ตรวจสอบ PVC
kubectl get pvc -n signoz
kubectl describe pvc -n signoz clickhouse-data-clickhouse-0

# ตรวจสอบ StorageClass
kubectl get storageclass
```

### OTEL Collector ไม่รับ data
```bash
# ตรวจสอบ service endpoint
kubectl get ep -n signoz signoz-otel-collector

# ทดสอบ connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  wget -O- http://signoz-otel-collector.signoz.svc.cluster.local:4318/v1/traces
```

## การลบ Deployment

```bash
# ลบด้วย kustomize
kubectl delete -k /home/cbe/sample-docker-image/k8s/signoz

# หรือลบ namespace ทั้งหมด
kubectl delete namespace signoz
```

## หมายเหตุ

- SigNoz Frontend เปิดให้เข้าถึงผ่าน NodePort 30301 (สามารถเปลี่ยนเป็น LoadBalancer หรือ Ingress ได้)
- ClickHouse จะเก็บข้อมูลใน PersistentVolume ดังนั้นข้อมูลจะไม่หายแม้ pod restart
- สำหรับ production แนะนำให้ใช้ external ClickHouse cluster และเพิ่ม authentication
- ควร configure retention policies สำหรับ ClickHouse เพื่อไม่ให้ storage เต็ม
