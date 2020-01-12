from rq import Worker, Queue, Connection

from app.app import redis

listen = ['high', 'default', 'low']

if __name__ == '__main__':
    with Connection(redis):
        worker = Worker(map(Queue, listen))
        worker.work()
