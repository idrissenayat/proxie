import http from 'k6/http';
import { check, sleep } from 'k6';

// Configuration: 100+ concurrent users for 2 minutes
export const options = {
    stages: [
        { duration: '30s', target: 50 },  // Ramp up to 50 users
        { duration: '1m', target: 100 }, // Stay at 100 users
        { duration: '30s', target: 0 },   // Ramp down to 0 users
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
        http_req_failed: ['rate<0.01'],    // Less than 1% errors
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const LOAD_TEST_SECRET = __ENV.LOAD_TEST_SECRET || 'proxie_load_test_key_2026';

export default function () {
    const params = {
        headers: {
            'X-Load-Test-Secret': LOAD_TEST_SECRET,
            'Authorization': 'Bearer mock-token',
            'X-Test-User-Role': 'consumer',
        },
    };

    // 1. Health Check (Public)
    const resReady = http.get(`${BASE_URL}/ready`);
    check(resReady, {
        'ready status is 200': (r) => r.status === 200,
    });

    // 2. Get Service Catalog (Public)
    const resCatalog = http.get(`${BASE_URL}/services/catalog/full`);
    check(resCatalog, {
        'catalog load is 200': (r) => r.status === 200,
    });

    // 3. List Providers (Protected - uses bypass)
    const resProviders = http.get(`${BASE_URL}/providers/`, params);
    check(resProviders, {
        'providers list is 200': (r) => r.status === 200,
    });

    // 4. List Consumer Requests (Protected - uses bypass)
    const resRequests = http.get(`${BASE_URL}/requests/`, params);
    check(resRequests, {
        'requests list is 200': (r) => r.status === 200,
    });

    sleep(1);
}
