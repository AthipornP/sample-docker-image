# SigNoz Deployment สำหรับ Kubernetes

## คำอธิบาย

SigNoz เป็น open-source observability platform ที่ใช้สำหรับ monitoring และ troubleshooting applications โดยรวบรวม:
- **Traces** - Distributed tracing
- **Metrics** - Application และ infrastructure metrics
- **Logs** - Centralized logging

## ⚠️ สถานะปัจจุบัน

**Deployment แบบ Manual นี้ยังไม่สมบูรณ์** - ขาด OTEL Collector ซึ่งเป็น component สำคัญในการรับ telemetry data จาก applications

### Components ที่มีอยู่:
- ✅ **ClickHouse** - Database สำหรับเก็บข้อมูล
- ✅ **Query Service** - Backend API
- ✅ **Frontend** - Web UI (เข้าถึงได้ที่ NodePort 30301)

### Components ที่ขาด:
- ❌ **OTEL Collector** - รับ telemetry data จาก applications (ซับซ้อนเกินไป)

## แนะนำ: ใช้ Helm Chart แทน

SigNoz มี official Helm chart ที่ configure ทุกอย่างอย่างถูกต้องแล้ว

### ติดตั้งด้วย Helm

```bash
# เพิ่ม Helm repository
helm repo add signoz https://charts.signoz.io
helm repo update

# ติดตั้ง SigNoz (self-hosted)
helm install signoz signoz/signoz \
  --namespace signoz \
  --create-namespace

# ดูสถานะ
kubectl get pods -n signoz
```

### การเข้าถึง UI

```bash
# Port forward
kubectl port-forward -n signoz svc/signoz-frontend 3301:3301

# เปิด browser ไปที่
http://localhost:3301
```

## Alternative: Deploy แบบ Manual (ไม่แนะนำ)

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
