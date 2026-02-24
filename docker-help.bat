@echo off
REM Hotel Concierge - Docker Helper Script for Windows
REM Usage: docker-help.bat [command]

setlocal enabledelayedexpansion

if "%1"=="" (
    call :print_help
    exit /b 0
)

if "%1"=="start" (
    echo Starting services...
    docker-compose up -d
    echo.
    echo Access the application:
    echo   Web UI: http://localhost:3000
    echo   Node.js API: http://localhost:3000/api
    echo   Python API: http://localhost:5000/api
    exit /b 0
)

if "%1"=="stop" (
    echo Stopping services...
    docker-compose down
    exit /b 0
)

if "%1"=="restart" (
    echo Restarting services...
    docker-compose restart
    exit /b 0
)

if "%1"=="build" (
    echo Building Docker images...
    docker-compose build
    exit /b 0
)

if "%1"=="logs" (
    docker-compose logs -f
    exit /b 0
)

if "%1"=="logs-node" (
    docker-compose logs -f nodejs-app
    exit /b 0
)

if "%1"=="logs-python" (
    docker-compose logs -f python-app
    exit /b 0
)

if "%1"=="logs-mysql" (
    docker-compose logs -f mysql-db
    exit /b 0
)

if "%1"=="ps" (
    docker-compose ps
    exit /b 0
)

if "%1"=="mysql" (
    echo Accessing MySQL database...
    docker exec -it hotel-concierge-mysql mysql -u root -ppassword hotel_concierge
    exit /b 0
)

if "%1"=="clean" (
    echo Removing containers and volumes...
    docker-compose down -v
    exit /b 0
)

if "%1"=="rebuild" (
    echo Rebuilding and starting services...
    docker-compose up --build -d
    echo.
    echo Access the application:
    echo   Web UI: http://localhost:3000
    exit /b 0
)

if "%1"=="health" (
    echo Checking service health...
    echo.
    docker-compose ps
    exit /b 0
)

if "%1"=="help" (
    call :print_help
    exit /b 0
)

echo Unknown command: %1
call :print_help
exit /b 1

:print_help
echo Hotel Concierge - Docker Helper
echo.
echo Usage: docker-help.bat [command]
echo.
echo Commands:
echo   start          - Start all services
echo   stop           - Stop all services
echo   restart        - Restart all services
echo   build          - Build Docker images
echo   logs           - View logs from all services
echo   logs-node      - View Node.js server logs
echo   logs-python    - View Python API logs
echo   logs-mysql     - View MySQL logs
echo   ps             - List running services
echo   mysql          - Access MySQL database
echo   clean          - Stop and remove volumes
echo   rebuild        - Rebuild images and start
echo   health         - Check service health
echo   help           - Show this help message
echo.
exit /b 0
