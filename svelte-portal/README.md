# Svelte Portal Docker Sample

นี่คือตัวอย่างการสร้าง Svelte application ที่รันใน Docker container

## ฟีเจอร์

- **Svelte Framework**: เฟรมเวิร์ค JavaScript ที่มีประสิทธิภาพสูง
- **Rollup Bundler**: เครื่องมือสำหรับ bundle และ optimize code
- **Docker Container**: รันบน Node.js 20 Alpine Linux
- **Static File Serving**: ใช้ sirv-cli สำหรับ serve static files
- **Responsive Design**: รองรับการแสดงผลบนหน้าจอขนาดต่างๆ

## การใช้งาน

### Build และ Run ด้วย Docker Compose
```bash
docker compose up --build
```

### เข้าดูเว็บไซต์
เปิดเบราว์เซอร์และไปที่ http://localhost:3000

### หยุดการทำงาน
```bash
docker compose down
```

## โครงสร้างไฟล์

```
svelte-portal/
├── src/
│   ├── App.svelte          # Main Svelte component
│   ├── Navbar.svelte       # Navigation component
│   └── main.js             # Entry point
├── public/
│   ├── index.html          # HTML template
│   ├── global.css          # Global styles
│   └── build/              # Built files (generated)
├── rollup.config.js        # Rollup configuration
├── package.json            # Dependencies และ scripts
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker compose configuration
└── README.md               # คู่มือนี้
```

## สิ่งที่เรียนรู้ได้

1. **Svelte Development**: การสร้าง component และ compile เป็น vanilla JavaScript
2. **Rollup Configuration**: การตั้งค่า bundler สำหรับ Svelte
3. **Docker Containerization**: การสร้าง container สำหรับ web application
4. **Static File Serving**: การ serve file จาก container
5. **Multi-stage Development**: การแยก development และ production environment

## เทคโนโลยีที่ใช้

- **Svelte 3.x**: Frontend framework
- **Rollup**: Module bundler
- **sirv-cli**: Static file server
- **Node.js 20**: Runtime environment
- **Alpine Linux**: Base container image
- **Docker & Docker Compose**: Containerization platform
