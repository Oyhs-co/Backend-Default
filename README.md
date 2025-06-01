# TaskHub Backend

TaskHub is a comprehensive project management platform built with a microservices architecture using Python, FastAPI, SQLAlchemy, and Supabase.

## Project Structure

taskhub/
├── api/
│   ├── __init__.py
│   ├── api-gateway/
│   │   ├── main.py
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py
│   │   │   └── circuit_breaker.py
│   │   └── utils/
│   │       └── service_registry.py
│   ├── auth-service/
│   │   └── app/
│   │       ├── main.py
│   │       ├── schemas/
│   │       │   └── user.py
│   │       └── services/
│   │           └── auth_service.py
│   ├── document-service/
│   │   └── app/
│   │       ├── main.py
│   │       ├── decorators/
│   │       │   └── document_decorators.py
│   │       ├── factories/
│   │       │   └── document_factory.py
│   │       ├── schemas/
│   │       │   └���─ document.py
│   │       └── services/
│   │           └── document_service.py
│   ├── external-tools-service/
│   │   └── app/
│   │       ├── main.py
│   │       ├── adapters/
│   │       │   └── oauth_adapter.py
│   │       ├── schemas/
│   │       │   └── external_tools.py
│   │       └── services/
│   │           └── external_tools_service.py
│   ├── notification-service/
│   │   └── app/
│   │       ├── main.py
│   │       ├── observers/
│   │       │   └── notification_observer.py
│   │       ├── schemas/
│   │       │   └── notification.py
│   │       └── services/
│   │           └── notification_service.py
│   ├── project-service/
│   │   └── app/
│   │       ├── main.py
│   │       ├── commands/
│   │       │   └── task_commands.py
│   │       ├── schemas/
│   │       │   ├── activity.py
│   │       │   ├── project.py
│   │       │   └── task.py
│   │       └── services/
│   │           ├── activity_service.py
│   │           ├── project_service.py
│   │           └── task_service.py
│   ├── shared/
│   │   ├── dtos/
│   │   │   ├── auth_dtos.py
│   │   │   ├── document_dtos.py
│   │   │   ├── external_tools_dtos.py
│   │   │   ├── notification_dtos.py
│   │   │   └── project_dtos.py
│   │   ├── exceptions/
│   │   │   ├── auth_exceptions.py
│   │   │   ├── base_exceptions.py
│   │   │   ├── document_exceptions.py
│   │   │   └── project_exceptions.py
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   ├── document.py
│   │   │   ├── external_tools.py
│   │   │   ├── notification.py
│   │   │   ├── project.py
│   │   │   └── user.py
│   │   └── utils/
│   │       ├── db.py
│   │       ├── jwt.py
│   │       ├── rabbitmq.py
│   │       └── supabase.py
│   └── tests/
│       ├── auth/
│       ├── document/
│       └── project/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md

## Microservices

### API Gateway

The API Gateway serves as the single entry point for all client requests. It routes requests to the appropriate microservice, handles authentication, and implements circuit breaker patterns for resilience.

### Auth Service

Manages user authentication and authorization using JWT tokens and Supabase Auth.

### Project Service

Handles project management, tasks, and activity tracking. Implements the Command pattern for undo/redo functionality.

### Document Service

Manages document storage, versioning, and permissions. Uses the Factory Method pattern for document creation and the Decorator pattern for additional functionality.

### Notification Service

Sends notifications through various channels (in-app, email, push, SMS) using the Observer pattern.

### External Tools Service

Integrates with external services like GitHub, Google Drive, etc. using the Adapter pattern.

## Design Patterns

- **Singleton**: Used for database and Supabase connections
- **Factory Method**: Used for document creation
- **Command**: Used for task operations with undo/redo functionality
- **Observer**: Used for notification delivery
- **Adapter**: Used for external tool integrations
- **Decorator**: Used for document functionality
- **Facade**: Used in the API Gateway
- **Circuit Breaker**: Used for service resilience

## User Roles

- **Admin**: Full access to all system features
- **Owner**: Full access to owned projects and their resources
- **Member**: Limited access based on project permissions

## Getting Started

### Prerequisites

- Python 3.13+
- Poetry
- Docker and Docker Compose
- Supabase account

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/taskhub.git
   cd taskhub
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Create a `.env` file based on `.env.example`:

   ```bash
   cp .env.example .env
   ```

4. Update the `.env` file with your Supabase credentials and other configuration.

### Running with Docker

```bash
docker-compose up -d
```

### Running Locally

1. Start the services individually:

   ```bash
   # Terminal 1
   uvicorn api.auth-service.app.main:app --host 0.0.0.0 --port 8001
   
   # Terminal 2
   uvicorn api.project-service.app.main:app --host 0.0.0.0 --port 8002
   
   # Terminal 3
   uvicorn api.document-service.app.main:app --host 0.0.0.0 --port 8003
   
   # Terminal 4
   uvicorn api.notification-service.app.main:app --host 0.0.0.0 --port 8004
   
   # Terminal 5
   uvicorn api.external-tools-service.app.main:app --host 0.0.0.0 --port 8005
   
   # Terminal 6
   uvicorn api.api-gateway.main:app --host 0.0.0.0 --port 8000
   ```

2. Access the API at `http://localhost:8000`

## API Documentation

Once the services are running, you can access the API documentation at:

- API Gateway: `http://localhost:8000/docs`
- Auth Service: `http://localhost:8001/docs`
- Project Service: `http://localhost:8002/docs`
- Document Service: `http://localhost:8003/docs`
- Notification Service: `http://localhost:8004/docs`
- External Tools Service: `http://localhost:8005/docs`

## Deployment

The application can be deployed to various cloud providers:

### AWS

1. Create an ECR repository for each service
2. Push Docker images to ECR
3. Deploy using ECS or EKS

### Azure

1. Create an Azure Container Registry
2. Push Docker images to ACR
3. Deploy using Azure Kubernetes Service or App Service

### Fly.io

1. Install the Fly CLI
2. Configure the `fly.toml` file
3. Deploy with `fly deploy`

## Security Recommendations

- Store sensitive tokens in a secure vault
- Implement proper token revocation
- Use HTTPS for all communications
- Encrypt sensitive data at rest
- Implement rate limiting
- Regularly rotate keys and credentials

## Architecture Advantages

- **Scalability**: Each microservice can be scaled independently
- **Resilience**: Circuit breaker pattern prevents cascading failures
- **Flexibility**: Services can be developed, deployed, and scaled independently
- **Technology Evolution**: Different services can adopt new technologies without affecting others
- **Team Organization**: Teams can work on different services in parallel

## License

This project is licensed under the MIT License - see the LICENSE file for details.
