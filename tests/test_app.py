import os
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from redis import Redis
from redis.exceptions import ConnectionError

from app import create_app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.store = Mock()
        with patch.dict(os.environ, {"CLUSTER_ID": "Test Cloud", "COUNTER_KEY": "test"}):
            self.client = create_app(self.store).test_client()

    def test_increments_every_visit(self):
        self.store.incr.side_effect = [41, 42]
        for count in (41, 42):
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["X-Cluster-ID"], "Test Cloud")
            self.assertIn(f'class="count">{count}<'.encode(), response.data)
        self.assertEqual(self.store.incr.call_count, 2)
        self.store.incr.assert_called_with("test")

    def test_health_and_readiness_without_increment(self):
        self.assertEqual(self.client.get("/healthz").status_code, 200)
        self.assertEqual(self.client.get("/readyz").status_code, 200)
        self.store.incr.assert_not_called()
        self.store.ping.assert_called_once()

    def test_redis_failure(self):
        self.store.ping.side_effect = self.store.incr.side_effect = ConnectionError()
        self.assertEqual(self.client.get("/").status_code, 503)
        self.assertEqual(self.client.get("/healthz").status_code, 200)
        self.assertEqual(self.client.get("/readyz").status_code, 503)

    def test_load_endpoint_requires_opt_in(self):
        with patch.dict(os.environ, {"ENABLE_LOAD_TEST": "0"}):
            self.assertEqual(create_app(self.store).test_client().get("/demo-load").status_code, 404)
        with patch.dict(os.environ, {"ENABLE_LOAD_TEST": "1"}):
            self.assertEqual(create_app(self.store).test_client().get("/demo-load").status_code, 204)
        self.store.incr.assert_not_called()


@unittest.skipUnless(os.getenv("TEST_REDIS_URL"), "set TEST_REDIS_URL for live Redis")
class RedisIntegrationTests(unittest.TestCase):
    def test_counter_shared_between_app_instances(self):
        store = Redis.from_url(os.environ["TEST_REDIS_URL"])
        key = f"vc-test:{uuid4()}"
        try:
            with patch.dict(os.environ, {"COUNTER_KEY": key}):
                first = create_app(store).test_client()
                second = create_app(store).test_client()
            self.assertIn(b'class="count">1<', first.get("/").data)
            self.assertIn(b'class="count">2<', second.get("/").data)
            self.assertEqual(store.get(key), b"2")
        finally:
            store.delete(key)
            store.close()
