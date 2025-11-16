#!/bin/bash

# Docker setup script for euro-camp

echo "🚀 Setting up euro-camp with Docker..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with required environment variables."
    exit 1
fi

# Build and start containers
echo "📦 Building Docker images..."
docker-compose build

echo "🏗️  Starting services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec web uv run python manage.py migrate

# Create superuser (optional)
echo ""
echo "Would you like to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker-compose exec web uv run python manage.py createsuperuser
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Your application is running at: http://localhost:8000"
echo "📚 API Documentation:"
echo "   - Swagger UI: http://localhost:8000/api/docs/"
echo "   - ReDoc: http://localhost:8000/api/redoc/"
echo "   - OpenAPI Schema: http://localhost:8000/api/schema/"
echo ""
echo "📋 Useful commands:"
echo "   docker-compose logs -f web    # View application logs"
echo "   docker-compose logs -f db     # View database logs"
echo "   docker-compose down           # Stop services"
echo "   docker-compose restart        # Restart services"
echo ""
