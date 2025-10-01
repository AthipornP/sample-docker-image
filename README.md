# Customer Portal Ecosystem

ระบบ Customer Portal พร้อม SSO (Single Sign-On) ที่ integrates กับ Keycloak สำหรับ authentication และ authorization ครอบคลุมทั้ง Web Applications และ REST APIs ในหลายภาษา

![Customer Portal Architecture](Customer-Portal.png)

## 📋 ภาพรวม

**Customer Portal** เป็น hub หลักที่เขียนด้วย Svelte ทำหน้าที่เป็นจุดเริ่มต้นในการเข้าถึงระบบต่างๆ ผ่าน **OAuth2/OIDC** โดยใช้ **Keycloak** เป็น Identity Provider

### สถาปัตยกรรม

```mermaid
---
title: Customer Portal Ecosystem
---
%%{init: {'flowchart': {'nodeSpacing': 30,'rankSpacing': 50}}}%%
flowchart TB
    %% Style definitions
    classDef portal fill:#2563eb,color:#ffffff,stroke:#1d4ed8,stroke-width:2px
    classDef auth fill:#166534,color:#ecfdf5,stroke:#14532d,stroke-width:1.5px
    classDef server fill:#0f172a,color:#f8fafc,stroke:#0891b2,stroke-width:1.5px
    classDef api fill:#f97316,color:#111827,stroke:#b45309,stroke-width:1.5px
    classDef hub fill:#e2e8f0,color:#0f172a,stroke:#94a3b8,stroke-dasharray:4 3,stroke-width:1px

    subgraph Portal[Customer Portal]
        P0["Svelte Portal<br/>Launch point for SSO demos"]
    end
    class P0 portal

    subgraph Identity[Single Sign-On]
        KC((Keycloak IdP<br/>OAuth2 / OIDC provider))
    end
    class KC auth

    subgraph Services[Protected Applications]

    
        subgraph ServerApps[Server Applications]
            N1[".NET 8 Sample<br/>Server UI"]
            D1["Django Web App<br/>Protected pages"]
            P1["PHP Sample App<br/>OIDC client"]
        end
        class D1,N1,P1 server

        subgraph ApiApps[API Applications]
            N2[".NET Minimal API<br/>Protected endpoints"]
            D2["Django REST API<br/>JWT protected endpoints"]
            P2["PHP API<br/>Token validation"]
        end
        class N2,D2,P2 api

    end

    SrvHub["Server App<br/>Entrypoint"]
    ApiHub["API Explorer<br/>Links"]
    SrvOIDC["Server OIDC<br/>Flow"]
    ApiOIDC["API JWT<br/>Flow"]
    class SrvHub,ApiHub,SrvOIDC,ApiOIDC hub

    %% Portal launches apps
    P0 -->|"Navigate"| SrvHub
    P0 -->|"API tester"| ApiHub
    %% P0 -.->|"OIDC docs"| KC
    SrvHub --> N1
    SrvHub --> D1
    SrvHub --> P1
    ApiHub --> N2
    ApiHub --> D2
    ApiHub --> P2

    %% OIDC flows
    N1 --> SrvOIDC
    D1 --> SrvOIDC
    P1 --> SrvOIDC
    P0 --> SrvOIDC
    SrvOIDC -->|"OIDC authentication"| KC
    KC -.->|"Tokens"| SrvOIDC
    N2 --> ApiOIDC
    D2 --> ApiOIDC
    P2 --> ApiOIDC
    ApiOIDC -->|"JWT validation"| KC
    KC -.->|"JWKS"| ApiOIDC
```

## 🏗️ โครงสร้างโปรเจค

### 🌐 Portal & Frontend
- **`svelte-portal/`** — Customer Portal หลัก (Svelte)
  - จุดเริ่มต้นสำหรับเข้าถึง Server Apps และ API Explorer
  - รองรับ SSO login ผ่าน Keycloak

### 🖥️ Server Applications (OIDC Flow)
- **`dotnet8/`** — .NET 8 Web App | Port: 5000
- **`django/`** — Django Web App | Port: 8000  
- **`php/`** — PHP OIDC Sample | Port: 8080

### 🔌 REST API Applications (JWT Validation)
- **`dotnet8-api/`** — .NET 8 Minimal API | Port: 5001
- **`django-api/`** — Django REST Framework | Port: 8001
- **`php-api/`** — PHP JWT API | Port: 8081

## 🔐 การทำงานของ Authentication

### Server Apps (Authorization Code Flow)
1. User คลิกเข้า app ผ่าน Portal
2. Redirect ไป Keycloak login
3. Keycloak ส่ง authorization code กลับมา
4. App แลก code เป็น access token
5. ใช้ token เข้าถึง protected pages

### REST APIs (JWT Bearer Token)
1. Client ส่ง request พร้อม `Authorization: Bearer <token>`
2. API validate JWT กับ Keycloak JWKS
3. ตรวจสอบ signature, expiration, issuer
4. อนุญาตเข้าถึง endpoint หรือ reject

## 🚀 การรันโปรเจค

### Prerequisites
- Docker & Docker Compose
- Keycloak ที่ configure แล้ว

### Quick Start

```powershell
# เข้าไปในโฟลเดอร์ของโปรเจคที่ต้องการ
cd svelte-portal

# Build และรัน container
docker compose up --build -d

# ดู logs
docker compose logs -f

# หยุด container
docker compose down
```

### ทดสอบทุกโปรเจค

| โปรเจค | คำสั่ง | URL |
|--------|--------|-----|
| Svelte Portal | `cd svelte-portal && docker compose up -d` | http://localhost:3000 |
| .NET App | `cd dotnet8 && docker compose up -d` | http://localhost:5000 |
| Django App | `cd django && docker compose up -d` | http://localhost:8000 |
| PHP App | `cd php && docker compose up -d` | http://localhost:8080 |
| .NET API | `cd dotnet8-api && docker compose up -d` | http://localhost:5001 |
| Django API | `cd django-api && docker compose up -d` | http://localhost:8001 |
| PHP API | `cd php-api && docker compose up -d` | http://localhost:8081 |

## 🛠️ Development Workflow

1. **แก้ไขโค้ด** ในโปรเจคที่ต้องการ
2. **Rebuild image** หลังแก้ไข
   ```powershell
   docker compose up --build -d
   ```
3. **ทดสอบด้วย curl** (ใช้ `curl.exe` บน Windows)
   ```powershell
   curl.exe -H "Authorization: Bearer <token>" http://localhost:5001/api/weather
   ```

## 🔧 Configuration

แต่ละโปรเจคมี `docker-compose.yml` และ environment variables สำหรับ:
- Keycloak connection (realm, client ID, secret)
- Database configuration
- Port mappings
- Volume mounts

ดูรายละเอียดใน `README.md` ของแต่ละโปรเจค

## 📦 Docker Images

ทุกโปรเจครองรับการรันในรูปแบบ container พร้อม:
- ✅ Multi-stage builds สำหรับ optimize size
- ✅ Health checks
- ✅ Environment-based configuration
- ✅ Volume mounts สำหรับ development

## 🔍 Debugging

```powershell
# ดู running containers
docker ps -a

# เข้าไปใน container
docker exec -it <container_name> /bin/bash

# ดู logs
docker compose logs -f <service_name>

# Restart service
docker compose restart <service_name>
```

## 📚 เอกสารเพิ่มเติม

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OAuth 2.0 / OIDC Spec](https://oauth.net/2/)
- แต่ละโปรเจคมี `README.md` เฉพาะที่อธิบายการ setup และ configuration

---

**Note:** ระบบนี้ออกแบบมาเพื่อเป็น demo และ learning purpose สำหรับการทำ SSO integration ในภาษาและ framework ต่างๆ
