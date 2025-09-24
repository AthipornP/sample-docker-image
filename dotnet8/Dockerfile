# Multi-stage Dockerfile for a .NET 8 ASP.NET Core app
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# copy csproj and restore first (better layer caching)
COPY SampleApp.csproj ./
RUN dotnet restore

# copy remaining sources
COPY . ./
RUN dotnet publish -c Release -o /app --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app .

ENTRYPOINT ["dotnet", "SampleApp.dll"]
