# PHP (plain) Docker example

This folder contains a minimal Docker example for a plain PHP site (no framework).

Files:
- `Dockerfile` - uses official PHP + Apache image.
- `docker-compose.yml` - builds the image and exposes it on port 8080.
- `index.php` - simple test page.

How to run:

1. Build and start:

   docker compose up --build

2. Open http://localhost:8080 in your browser.

Notes:
- For connecting to databases (MySQL/Postgres), add a `db` service in `docker-compose.yml` and install the appropriate PHP extensions.
- In production, avoid mounting source and use COPY in Dockerfile to ensure immutable images.
