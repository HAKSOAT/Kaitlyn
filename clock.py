from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue

from main import run, redis

q = Queue(connection=redis)


# Create a schedule to run Kaitlyn
scheduler = BlockingScheduler()
scheduler.add_job(func=q.enqueue, trigger="interval", args=[run], seconds=30)
scheduler.start()
