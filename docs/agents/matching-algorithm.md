# Matching Algorithm

## Overview

The matching algorithm connects service requests with relevant providers.

## Matching Pipeline

```
1. FILTER - Hard constraints (must match)
2. SCORE - Soft factors (ranking)
3. RANK - Order by score
4. ROUTE - Send to top N provider agents
```

## Filter Stage

Remove providers who don't meet basic requirements:

| Criterion | Logic |
|-----------|-------|
| Service category | Must offer the service |
| Location | Within service radius of request |
| Availability | Has slots matching request timing |
| Status | Must be "active" |

## Score Stage

Score remaining providers on fit:

| Factor | Weight | Scoring |
|--------|--------|---------|
| Specialization match | 30% | % of requested specializations provider has |
| Distance | 20% | Closer is better |
| Availability fit | 20% | More matching slots is better |
| Rating | 15% | Higher is better |
| Price fit | 15% | Within budget scores higher |

## Rank Stage

Sort providers by total score, descending.

## Route Stage

Send request to top N providers (default: 10).

Provider agents then decide whether to make an offer.

## Future Improvements

- Semantic matching using embeddings
- Learning from booking patterns
- Provider preference learning
