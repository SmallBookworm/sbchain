import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
def job1():
    print('job1', datetime.datetime.now())

scheduler = BlockingScheduler()

scheduler.add_job(job1, 'interval', seconds=2, id='job1')  # 每隔5秒执行一次

scheduler.start()