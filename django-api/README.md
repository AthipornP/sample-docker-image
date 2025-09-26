# Django REST API with Keycloak JWT Authentication

Django REST API ที่ implement JWT authentication โดยใช้ public key จาก Keycloak และมี endpoint สำหรับดึงข้อมูลสภาพอากาศ

## Features

- JWT Authentication ด้วย Keycloak public key
- Weather API integration (Bangkok weather from goweather.xyz)
- User profile endpoint
- Health check endpoint
- CORS support
- Docker containerization

## API Endpoints

### Public Endpoints
- `GET /api/health/` - Health check endpoint

### Protected Endpoints (ต้องใช้ JWT token)
- `GET /api/profile/` - ดูข้อมูล user profile จาก JWT token
- `GET /api/weather/bangkok/` - ดึงข้อมูลสภาพอากาศ Bangkok

## Authentication

API ใช้ JWT authentication โดยตรวจสอบ token กับ public key จาก Keycloak:
- Keycloak URL: `https://s02.iampm.online/realms/master`
- JWKS URL: `https://s02.iampm.online/realms/master/protocol/openid_connect/certs`

### การใช้งาน

1. ส่ง JWT token ใน Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

2. Token จะถูกตรวจสอบด้วย public key จาก Keycloak

## Installation & Usage

### Development (Local)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start development server:
```bash
python manage.py runserver 0.0.0.0:8000
```

### Docker

1. Build and run with docker-compose:
```bash
docker-compose up --build
```

2. API จะรันที่ port 8001: http://localhost:8001

## Testing

### ทดสอบด้วย curl

1. Health Check (ไม่ต้องใช้ token):
```bash
curl.exe -X GET http://localhost:8001/api/health/
```

2. ทดสอบด้วย JWT token จาก Customer Portal:
```bash
curl.exe -X GET http://localhost:8001/api/profile/ -H "Authorization: Bearer <your-jwt-token>"
```

3. ดึงข้อมูลสภาพอากาศ Bangkok:
```bash
curl.exe -X GET http://localhost:8001/api/weather/bangkok/ -H "Authorization: Bearer <your-jwt-token>"
```

## Configuration

### Environment Variables

- `DEBUG`: Django debug mode (default: True)
- `DJANGO_SETTINGS_MODULE`: Django settings module (default: config.settings)

### Keycloak Settings

Configuration ใน `config/settings.py`:
```python
KEYCLOAK_URL = 'https://s02.iampm.online/realms/master'
KEYCLOAK_CERT_URL = f'{KEYCLOAK_URL}/protocol/openid_connect/certs'
```

## Project Structure

```
django-api/
├── config/                 # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── api/                    # API application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── authentication.py   # Keycloak JWT authentication
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py           # API endpoints
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker compose configuration
├── docker-entrypoint.sh   # Docker entrypoint script
└── README.md              # This file
```

## Dependencies

- Django 4.2.7
- Django REST Framework 3.14.0
- PyJWT 2.8.0
- python-jose[cryptography] 3.3.0
- requests 2.31.0
- django-cors-headers 4.3.1

## License

MIT License