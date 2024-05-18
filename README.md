# Flask Prediction App with Redis and RQ

This application uses Redis and Redis Queue (RQ) as its message broker. The architecture ensures that the web app, Redis server, and worker are all running in separate containers, providing division and fault tolerance for our application. This setup also ensures that the load of running predictions does not fall on the web app.

### Prerequisites

- Docker
- Docker Compose

## Running the Application

To start the application, simply run the following command:

```bash
docker-compose up --build
