# .NET 8 Docker example

This folder contains a minimal example for packaging a .NET 8 ASP.NET Core application with Docker.

Files:
- `Dockerfile` - multi-stage build (sdk -> aspnet runtime).
- `docker-compose.yml` - simple compose file exposing port 5000 on the host.

How to build and run:

1. Build the image with Docker Compose:

   docker compose build

2. Run the service:

   docker compose up

Notes:
- Replace `YourApp.dll` in the `ENTRYPOINT` of the `Dockerfile` with your actual assembly name produced by `dotnet publish`.
- For production images, remove the source mount and ensure the app is published into the `/app` folder during the build stage.
