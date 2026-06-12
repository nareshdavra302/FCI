### What can be improved?

- Add client side tooling for ingesting pipelines
  - add middware package for ingesting failures
  - add a client side binary for listing to files and ingesting
  - add CDC for ingesting failures if some service loggs into database
  - add Message queue ingestion (Kafka/RabbitMQ) for ingesting failures
- write unit & integration tests for the backend
- add rate limiting for the API
- add a circuit breaker for the API
- add a Notification service, to send notifications to the users with what failed and how to fix it
- Async background workers for insights analysis
- Prometheus metrics endpoint for insights of backend performance
- OpenTelemetry tracing
- Auth on FCI API
- Refine search add elasticsearch for faster search
- add a Caching layer for the LLM API for analysis results to reduce token usage
- add support for Multiple LLM providers later if needed
