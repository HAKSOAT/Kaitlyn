from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue

from app.app import run
from app.config import redis

q = Queue(connection=redis)

scheduler = BlockingScheduler()
scheduler.add_job(func=q.enqueue, trigger="interval", args=[run], seconds=30)
scheduler.start()
