# Sample Docker Image collection

โฟลเดอร์นี้เก็บตัวอย่างการตั้งค่า Docker สำหรับ 3 โปรเจคตัวอย่างที่พร้อมรันบนเครื่องพัฒนาและสามารถ deploy ขึ้น Ubuntu server ที่ติดตั้ง Docker ไว้แล้วได้

โปรเจคที่มี:
- `dotnet8/` — ตัวอย่าง .NET 8 (minimal Web API) | port: host 5000 -> container 80
- `django/` — ตัวอย่าง Django (Gunicorn + Postgres) | port: host 8000 -> container 8000
- `php-plain/` — ตัวอย่าง PHP แบบไม่ใช้ framework (Apache + PHP) | port: host 8080 -> container 80

สรุปวิธีทดสอบ (บนเครื่องที่มี Docker / Docker Compose):

1) .NET 8

   cd dotnet8
   docker compose up --build -d

   ตรวจสอบหน้าเว็บ:

   - http://localhost:5000/

2) Django

   cd django
   docker compose up --build -d

   ตรวจสอบหน้าเว็บ:

   - http://localhost:8000/

   ถ้าต้องรัน migrations:

   docker compose run --rm web python manage.py migrate

3) PHP (plain)

   cd php-plain
   docker compose up --build -d

   ตรวจสอบหน้าเว็บ:

   - http://localhost:8080/

หยุดและลบ containers (cleanup):

   docker compose down --volumes

ข้อควรระวังสำหรับการ deploy ขึ้น Ubuntu server:
- ทางเลือกการ deploy:
  - Build บน server โดยตรง (git clone แล้ว `docker compose up --build -d`).
  - Build locally, push image ไปที่ registry (Docker Hub / private registry) แล้วบน server `docker pull` + `docker compose up -d`.
- เก็บความลับ (SECRET_KEY, DB passwords) ไว้นอก repository — ใช้ environment variables, `.env` (ไม่ commit) หรือ Docker secrets.
- สำหรับ production:
  - เพิ่ม healthchecks ใน Dockerfile / docker-compose
  - จัดการ static files ของ Django (`collectstatic`) และตั้งค่า reverse proxy (nginx) ถ้าจำเป็น
  - ใช้ systemd หรือ container orchestrator (kubernetes, docker swarm) สำหรับ auto-start และ recovery

---
Generated samples: dotnet8, django, php-plain — ทดสอบการรันด้วย `docker compose up --build -d` ตามที่อธิบายด้านบน
