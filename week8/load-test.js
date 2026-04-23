import http from 'k6/http';
import { check, sleep } from 'k6';

// options la cau hinh chung cho bai test.
// k6 se doc object nay truoc khi chay.
export const options = {
  vus: 300,
  duration: '10s',
  thresholds: {
    // Ti le request loi phai nho hon 1%.
    http_req_failed: ['rate<0.01'],
    // 95% request phai nhanh hon 500ms.
    http_req_duration: ['p(95)<500'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8080/api/v1';

// default function la ham ma moi virtual user (VU) se lap lai lien tuc
// trong suot thoi gian test.
export default function () {

  const getBooksResponse = http.get(`${BASE_URL}/books`);

  // check() dung de xac minh response co dat yeu cau khong.
  // Neu check fail, k6 van chay tiep nhung se ghi nhan loi vao ket qua.
  check(getBooksResponse, {
    'GET /books status is 200': (r) => r.status === 200,
    'GET /books response time < 500ms': (r) => r.timings.duration < 500,
  });

  // 2) Goi them API POST de mo phong hanh vi tao du lieu.
  const payload = JSON.stringify({
    title: 'Load Testing Book',
    author: 'k6',
    price: 19.99,
    publishedYear: 2026,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const createBookResponse = http.post(`${BASE_URL}/books`, payload, params);

  check(createBookResponse, {
    'POST /books status is 201': (r) => r.status === 201,
    'POST /books response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
