# Proxie Load Testing

This directory contains `k6` scripts for performance and load testing of the Proxie API.

## Prerequisites

1.  **Install k6**:
    *   macOS: `brew install k6`
    *   Docker: `docker pull grafana/k6`
    *   Other: [k6 Installation Guide](https://k6.io/docs/getting-started/installation/)

## Running Locally

To run a basic load test against your local development server:

```bash
# Ensure your API is running first (source venv/bin/activate && uvicorn src.platform.main:app)
k6 run tests/load/load_test.js
```

### Customizing the Target

You can point to a different environment (e.g., staging) using environment variables:

```bash
k6 run -e BASE_URL=https://api.staging.proxie.app tests/load/load_test.js
```

## Security Note

The load test uses an authentication bypass mechanism enabled only in `testing` and `development` environments. It requires the `X-Load-Test-Secret` header to match the `LOAD_TEST_SECRET` configured in the backend settings.

## Scenarios Covered

*   **Ramp-up**: 0 to 50 users in 30s.
*   **Peak Load**: Steady 100 concurrent users for 1 minute.
*   **Ramp-down**: 100 to 0 users in 30s.

## Thresholds

*   **Latency**: 95% of requests must be under **500ms**.
*   **Error Rate**: Must be less than **1%**.
