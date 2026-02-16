"""Helper to run an RQ worker in the app context when using Docker or locally.
Run with: python backend/worker.py
"""
import os
import sys
from rq import Connection, Worker
import redis

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        qs = ['default']
        w = Worker(qs)
        w.work()
