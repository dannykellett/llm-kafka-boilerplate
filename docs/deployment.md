# Deployment Documentation

This document provides instructions for deploying the LLM-Kafka Boilerplate in various environments, including local development, Docker, and Kubernetes.

## Prerequisites

Before deploying the application, ensure you have:

1. Access to a Kafka cluster
2. API key for an LLM service (OpenAI, OpenRouter, etc.)
3. Python 3.12 or higher (for local deployment)
4. Docker and Docker Compose (for containerized deployment)
5. Kubernetes cluster (for Kubernetes deployment)

## Local Deployment

### 1. Set Up Environment

1. Clone the repository:

```bash
git clone https://github.com/yourusername/llm-kafka-boilerplate.git
cd llm-kafka-boilerplate
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
uv pip install .
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with your configuration:

```
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_INPUT_TOPIC=input-topic
KAFKA_OUTPUT_TOPIC=output-topic
KAFKA_GROUP_ID=my-consumer-group
KAFKA_AUTO_OFFSET_RESET=earliest
KAFKA_ENABLE_AUTO_COMMIT=true

# LLM Configuration
LLM_API_KEY=your-api-key
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=500

# Application Configuration
LOG_LEVEL=INFO
CACHE_TTL_SECONDS=3600
```

### 3. Run the Application

```bash
python -m src
```

## Docker Deployment

### 1. Build Docker Image

```bash
docker build -t llm-kafka-boilerplate .
```

### 2. Run Docker Container

```bash
docker run --env-file .env llm-kafka-boilerplate
```

### 3. Using Docker Compose

1. Configure environment variables in `.env` file (same as local deployment)

2. Run with Docker Compose:

```bash
docker-compose up -d
```

3. Check logs:

```bash
docker-compose logs -f
```

4. Stop the application:

```bash
docker-compose down
```

## Kubernetes Deployment

### 1. Create Kubernetes ConfigMap and Secret

1. Create a ConfigMap for non-sensitive configuration:

```yaml
# config-map.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-kafka-config
data:
  KAFKA_BOOTSTRAP_SERVERS: "kafka-service:9092"
  KAFKA_INPUT_TOPIC: "input-topic"
  KAFKA_OUTPUT_TOPIC: "output-topic"
  KAFKA_GROUP_ID: "my-consumer-group"
  KAFKA_AUTO_OFFSET_RESET: "earliest"
  KAFKA_ENABLE_AUTO_COMMIT: "true"
  LOG_LEVEL: "INFO"
  CACHE_TTL_SECONDS: "3600"
```

2. Create a Secret for sensitive configuration:

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: llm-kafka-secret
type: Opaque
stringData:
  LLM_API_KEY: "your-api-key"
  LLM_API_URL: "https://api.openai.com/v1/chat/completions"
  LLM_MODEL: "gpt-4"
  LLM_TEMPERATURE: "0.2"
  LLM_MAX_TOKENS: "500"
```

3. Apply the ConfigMap and Secret:

```bash
kubectl apply -f config-map.yaml
kubectl apply -f secret.yaml
```

### 2. Create Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-kafka-boilerplate
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llm-kafka-boilerplate
  template:
    metadata:
      labels:
        app: llm-kafka-boilerplate
    spec:
      containers:
      - name: llm-kafka-boilerplate
        image: llm-kafka-boilerplate:latest
        imagePullPolicy: IfNotPresent
        envFrom:
        - configMapRef:
            name: llm-kafka-config
        - secretRef:
            name: llm-kafka-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

3. Apply the Deployment:

```bash
kubectl apply -f deployment.yaml
```

### 3. Monitor the Deployment

```bash
# Check deployment status
kubectl get deployments

# Check pods
kubectl get pods

# Check logs
kubectl logs -l app=llm-kafka-boilerplate

# Describe a pod
kubectl describe pod <pod-name>
```

## Scaling Considerations

### Horizontal Scaling

The application is designed to be horizontally scalable:

1. **Kafka Consumer Groups**: Multiple instances can be part of the same consumer group, and Kafka will distribute partitions among them.

2. **Stateless Design**: The application is stateless, so you can run multiple instances without conflicts.

3. **Rate Limiting**: The application implements rate limiting to ensure LLM API limits are respected across instances.

To scale horizontally:

- In Docker Compose:

```bash
docker-compose up -d --scale app=3
```

- In Kubernetes:

```bash
kubectl scale deployment llm-kafka-boilerplate --replicas=5
```

### Vertical Scaling

If you need to allocate more resources to each instance:

- In Docker:

```bash
docker run --env-file .env --memory=1g --cpus=2 llm-kafka-boilerplate
```

- In Kubernetes, update the resource requests and limits in the deployment.yaml file.

## Monitoring and Logging

### Logging

The application uses Python's logging module with configurable log levels. Logs are sent to stdout/stderr, which can be captured by container orchestration systems.

To view logs:

- In Docker:

```bash
docker logs <container-id>
```

- In Docker Compose:

```bash
docker-compose logs -f
```

- In Kubernetes:

```bash
kubectl logs -l app=llm-kafka-boilerplate
```

### Monitoring

For production deployments, consider integrating with monitoring systems:

1. **Prometheus**: Add a Prometheus client to expose metrics
2. **Grafana**: Create dashboards to visualize metrics
3. **ELK Stack**: Collect and analyze logs
4. **Datadog/New Relic**: For comprehensive application performance monitoring

## Troubleshooting

### Common Issues

1. **Kafka Connection Issues**:
   - Ensure Kafka is running and accessible
   - Check network connectivity
   - Verify bootstrap servers configuration

2. **LLM API Issues**:
   - Verify API key is correct
   - Check rate limits
   - Ensure API URL is correct

3. **Application Crashes**:
   - Check logs for error messages
   - Verify environment variables
   - Ensure sufficient resources are allocated

### Debugging

1. Set `LOG_LEVEL=DEBUG` for more detailed logs
2. Use the `--env` flag with Docker to override environment variables
3. Use `kubectl exec -it <pod-name> -- /bin/bash` to get a shell in a Kubernetes pod