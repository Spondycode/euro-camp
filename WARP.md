# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

euro-camp is a Django 5.2.7 REST API project with JWT and OAuth2 authentication, built for managing user accounts with role-based permissions. The project uses PostgreSQL as its database and follows a modular Django app structure.

## Development Setup

This project uses **UV** for dependency management (not pip). UV is a fast Python package installer and resolver.

### Initial Setup
```bash
# Install dependencies
uv sync

# Set up database (ensure PostgreSQL is running)
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Run development server
uv run python manage.py runserver
```

### Environment Configuration
The project uses a `.env` file in the root directory with the following variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_NAME`: PostgreSQL database name (default: euro_camp_db)
- `DATABASE_USER`: PostgreSQL user
- `DATABASE_PASSWORD`: PostgreSQL password
- `DATABASE_HOST`: Database host (default: localhost)
- `DATABASE_PORT`: Database port (default: 5432)
- `CORS_ALLOW_ALL_ORIGINS`: Enable CORS for all origins (True/False)

## Common Commands

### Development Server
```bash
# Run development server
uv run python manage.py runserver

# Run on specific port
uv run python manage.py runserver 8080
```

### Database Management
```bash
# Create migrations after model changes
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Open database shell
uv run python manage.py dbshell

# Show migration status
uv run python manage.py showmigrations
```

### Testing
```bash
# Run all tests
uv run python manage.py test

# Run tests for specific app
uv run python manage.py test accounts
uv run python manage.py test api
uv run python manage.py test core

# Run specific test case
uv run python manage.py test accounts.tests.TestClassName
```

### Django Shell
```bash
# Open Django shell for interactive testing
uv run python manage.py shell
```

### User Management
```bash
# Create superuser
uv run python manage.py createsuperuser

# Change user password
uv run python manage.py changepassword <username>
```

## Architecture

### App Structure

**config/**: Project configuration
- `settings.py`: Django settings, including REST Framework, JWT, OAuth2, and CORS configuration
- `urls.py`: Root URL configuration, includes API documentation endpoints

**accounts/**: Custom user authentication and authorization
- Custom `User` model extending `AbstractUser` with role-based permissions
- Three user roles: `SUPER_ADMIN`, `PAGE_ADMIN`, `USER`
- `is_super_admin` property for permission checking
- Custom UserAdmin for Django admin interface

**api/**: REST API endpoints
- Main API routing hub
- Currently includes health check endpoint at `/api/health/`
- Add new API endpoints here

**core/**: Core application functionality
- Placeholder for shared models, utilities, and core business logic

### Authentication

The project supports multiple authentication methods:

1. **JWT (Simple JWT)**
   - Access tokens: 30-minute lifetime
   - Refresh tokens: 1-day lifetime
   - Endpoints: `/api/auth/jwt/create/`, `/api/auth/jwt/refresh/`

2. **OAuth2 (django-oauth-toolkit)**
   - Access token expiration: 1 hour
   - OAuth2 endpoints available at `/o/`

3. **Session Authentication** (for Django admin)

### API Documentation

API documentation is auto-generated using drf-spectacular:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Custom User Model

The project uses a custom User model (`accounts.User`) instead of Django's default User model. Always reference users via:
```python
from accounts.models import User
# or
from django.contrib.auth import get_user_model
User = get_user_model()
```

### CORS Configuration

CORS is enabled via `django-cors-headers`. By default, all origins are allowed in development. Configure via `CORS_ALLOW_ALL_ORIGINS` and `CORS_ALLOWED_ORIGINS` in `.env`.

## Key Dependencies

- **Django 5.2.7**: Web framework
- **Django REST Framework**: REST API toolkit
- **djangorestframework-simplejwt**: JWT authentication
- **django-oauth-toolkit**: OAuth2 provider
- **drf-spectacular**: OpenAPI 3.0 schema generation
- **psycopg2-binary**: PostgreSQL adapter
- **django-cors-headers**: CORS middleware
- **python-dotenv**: Environment variable management

## Adding New Features

### Creating a New Django App
```bash
uv run python manage.py startapp <app_name>
```
Then add the app to `INSTALLED_APPS` in `config/settings.py`.

### Adding API Endpoints
1. Create views in `api/views.py` (or in respective app)
2. Add URL patterns to `api/urls.py` or app-specific urls.py
3. Create serializers if needed
4. API documentation will be auto-generated via drf-spectacular

### Database Schema Changes
1. Modify models in relevant app
2. Run `uv run python manage.py makemigrations`
3. Review generated migration files
4. Apply with `uv run python manage.py migrate`
