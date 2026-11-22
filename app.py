"""Flask visitor counter backed by a shared Redis key."""
import os

from flask import Flask, jsonify, render_template
from redis import Redis
from redis.exceptions import RedisError
from redis.backoff import NoBackoff
from redis.retry import Retry


def create_app(counter_store=None):
    app = Flask(__name__)
    cluster = os.getenv("CLUSTER_ID", "Local")
    key = os.getenv("COUNTER_KEY", "visitor-count")
    store = counter_store if counter_store is not None else Redis.from_url(
        os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
        retry=Retry(NoBackoff(), 0),
    )

    @app.after_request
    def identify(response):
        response.headers["X-Cluster-ID"] = cluster
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def home():
        try:
            count = store.incr(key)
        except RedisError:
            app.logger.warning("Redis counter unavailable")
            return render_template("index.html", cluster=cluster, count=None), 503
        return render_template("index.html", cluster=cluster, count=count)

    @app.get("/healthz")
    def health():
        return jsonify(status="ok")

    @app.get("/readyz")
    def ready():
        try:
            store.ping()
        except RedisError:
            return jsonify(status="unavailable"), 503
        return jsonify(status="ready")

    if os.getenv("ENABLE_LOAD_TEST") == "1":
        @app.get("/demo-load")
        def demo_load():
            # Fixed CPU workload for the local HPA experiment.
            import hashlib
            hashlib.pbkdf2_hmac("sha256", b"local-demo", b"visitor-counter", 80_000)
            return "", 204

    return app


app = create_app()
