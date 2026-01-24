# Internal API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health

#### GET /
Health check.

#### GET /health
Detailed health check.

### Providers

#### GET /providers
List providers.

#### POST /providers
Create provider.

#### GET /providers/{id}
Get provider by ID.

#### PUT /providers/{id}
Update provider.

#### POST /providers/{id}/services
Add a service to a provider.

#### GET /providers/{id}/services
List provider services.

### Requests

#### GET /requests
List service requests (supports `?status=` filtering).

#### POST /requests
Create service request.

#### GET /requests/{id}
Get request by ID.

#### GET /requests/{id}/offers
Get offers for request.

### Offers

#### POST /offers
Create offer.

#### PUT /offers/{id}/accept
Accept offer.

### Bookings

#### GET /bookings/{id}
Get booking by ID.

#### PUT /bookings/{id}/complete
Mark booking complete.

#### PUT /bookings/{id}/cancel
Cancel booking.

### Reviews

#### POST /reviews
Create review.

---

Full OpenAPI spec available at `/docs` when server is running.
