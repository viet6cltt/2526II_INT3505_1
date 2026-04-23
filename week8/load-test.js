import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,          // 10 virtual users
  duration: '10s',  // chạy 10 giây
  thresholds: {
    http_req_failed: ['rate<0.01'],     // error rate < 1%
    http_req_duration: ['p(95)<500'],   // 95% request < 500ms
  },
};

const BASE_URL = 'http://127.0.0.1:8080/api/v1';

export default function () {
  const res = http.get(`${BASE_URL}/books`);

  check(res, {
    'GET /books status is 200': (r) => r.status === 200,
    'GET /books response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}