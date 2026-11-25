import os
import socket

import redis
from flask import Flask, jsonify

app = Flask(__name__)

r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", "6379")),
    password=os.environ.get("REDIS_PASSWORD") or None,
    ssl=os.environ.get("REDIS_TLS", "false").lower() == "true",
    socket_connect_timeout=2,
    socket_timeout=2,
)


@app.get("/")
def index():
    hits = r.incr("hits")
    return jsonify(hits=hits, served_by=socket.gethostname())


@app.get("/healthz")
def healthz():
    """Liveness: the process is up and able to serve HTTP."""
    return "ok", 200


@app.get("/readyz")
def readyz():
    """Readiness: the process can reach its dependencies."""
    try:
        r.ping()
    except redis.RedisError as e:
        app.logger.warning("readiness check failed: %s", e)
        return jsonify(ready=False, error=str(e)), 503
    return jsonify(ready=True)
