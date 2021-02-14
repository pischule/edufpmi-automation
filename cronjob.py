from apscheduler.schedulers.blocking import BlockingScheduler
import os
from edufpmi_client import EdufpmiClient
import pytz
from datetime import datetime
import logging

ec = EdufpmiClient(os.environ['EDU_USERNAME'], os.environ['EDU_PASSWORD'])
tz = pytz.timezone('Europe/Minsk')


def run():
    minsk_now = datetime.now(tz)
    logging.info(f'time at minsk: {minsk_now.hour}.{minsk_now.minute}')
    if 8 < minsk_now.hour < 21 and minsk_now.weekday() != 6:
        ec.login()
        ec.check_all_attendance()
    else:
        logging.info("time restriction")


scheduler = BlockingScheduler()
scheduler.add_job(run, "interval", minutes=20)

scheduler.start()
