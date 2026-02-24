#!/bin/bash

# Hotel Concierge - Docker Helper Script
# Usage: ./docker-help.sh [command]

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_help() {
    echo -e "${CYAN}Hotel Concierge - Docker Helper${NC}"
    echo ""
    echo "Usage: ./docker-help.sh [command]"
    echo ""
    echo -e "${GREEN}Commands:${NC}"
    echo "  start          - Start all services"
    echo "  stop           - Stop all services"
    echo "  restart        - Restart all services"
    echo "  build          - Build Docker images"
    echo "  logs           - View logs from all services"
    echo "  logs-node      - View Node.js server logs"
    echo "  logs-python    - View Python API logs"
    echo "  logs-mysql     - View MySQL logs"
    echo "  ps             - List running services"
    echo "  mysql          - Access MySQL database"
    echo "  clean          - Stop and remove volumes"
    echo "  rebuild        - Rebuild images and start"
    echo "  health         - Check service health"
    echo "  help           - Show this help message"
    echo ""
}

case "$1" in
    start)
        echo -e "${YELLOW}Starting services...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✓ Services started${NC}"
        echo ""
        echo "Access the application:"
        echo "  Web UI: http://localhost:3000"
        echo "  Node.js API: http://localhost:3000/api"
        echo "  Python API: http://localhost:5000/api"
        ;;
    stop)
        echo -e "${YELLOW}Stopping services...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ Services stopped${NC}"
        ;;
    restart)
        echo -e "${YELLOW}Restarting services...${NC}"
        docker-compose restart
        echo -e "${GREEN}✓ Services restarted${NC}"
        ;;
    build)
        echo -e "${YELLOW}Building Docker images...${NC}"
        docker-compose build
        echo -e "${GREEN}✓ Images built${NC}"
        ;;
    logs)
        docker-compose logs -f
        ;;
    logs-node)
        docker-compose logs -f nodejs-app
        ;;
    logs-python)
        docker-compose logs -f python-app
        ;;
    logs-mysql)
        docker-compose logs -f mysql-db
        ;;
    ps)
        docker-compose ps
        ;;
    mysql)
        echo -e "${YELLOW}Accessing MySQL database...${NC}"
        docker exec -it hotel-concierge-mysql mysql -u root -ppassword hotel_concierge
        ;;
    clean)
        echo -e "${YELLOW}Removing containers and volumes...${NC}"
        docker-compose down -v
        echo -e "${GREEN}✓ Cleaned up${NC}"
        ;;
    rebuild)
        echo -e "${YELLOW}Rebuilding and starting services...${NC}"
        docker-compose up --build -d
        echo -e "${GREEN}✓ Services rebuilt and started${NC}"
        echo ""
        echo "Access the application:"
        echo "  Web UI: http://localhost:3000"
        ;;
    health)
        echo -e "${YELLOW}Checking service health...${NC}"
        echo ""
        echo "Services status:"
        docker-compose ps
        echo ""
        echo "Health check results:"
        docker-compose ps --services | while read service; do
            status=$(docker inspect hotel-concierge-$service 2>/dev/null | grep -o '"Health": "[^"]*' | cut -d'"' -f4 || echo "N/A")
            echo "  $service: $status"
        done
        ;;
    help|--help|-h|"")
        print_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        print_help
        exit 1
        ;;
esac
