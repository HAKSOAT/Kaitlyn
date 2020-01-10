import atexit

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

from main import run

app = Flask(__name__)

# Create a schedule to run Kaitlyn
scheduler = BackgroundScheduler()
scheduler.add_job(func=run, trigger="interval", seconds=30)
# Starts the schedule
scheduler.start()

# Shuts down scheduler before file exists
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(use_reloader=False)
