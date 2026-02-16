import threading
import uuid
from typing import Callable, Any, Dict
import os

_tasks: Dict[str, Dict] = {}

# Try to use RQ/Redis if available
_USE_RQ = False
try:
    import redis
    from rq import Queue
    _redis_conn = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
    _rq_queue = Queue(connection=_redis_conn)
    _USE_RQ = True
except Exception:
    _USE_RQ = False


def start_task(fn: Callable, *args, **kwargs) -> str:
    task_id = str(uuid.uuid4())
    _tasks[task_id] = {"status": "pending", "result": None, "error": None}

    if _USE_RQ:
        # enqueue to RQ
        job = _rq_queue.enqueue(fn, *args, **kwargs)
        _tasks[task_id] = {"status": "queued", "job_id": job.get_id()}
        return task_id

    def runner():
        _tasks[task_id]["status"] = "running"
        try:
            res = fn(*args, **kwargs)
            _tasks[task_id]["status"] = "completed"
            _tasks[task_id]["result"] = res
        except Exception as e:
            _tasks[task_id]["status"] = "failed"
            _tasks[task_id]["error"] = str(e)

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    return task_id


def get_task(task_id: str):
    t = _tasks.get(task_id)
    if not t and _USE_RQ:
        # try to map from RQ job id stored in tasks values
        # if RQ used, tasks store {'job_id': <id>}
        for k, v in _tasks.items():
            if v.get('job_id') == task_id:
                return v
    return t
