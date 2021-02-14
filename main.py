import time
import argparse
import logging
from datetime import datetime
from edufpmi_client import EdufpmiClient


class EdufpmiAutomator:
    def __init__(self, username, password, sleep=60 * 20):
        self.client = EdufpmiClient(username, password)
        self.sleep = sleep

    def start(self):

        while True:
            now = datetime.now()
            if now.weekday() == 6 or now.hour < 8 or now.hour > 21:
                logging.info('time restriction')
                time.sleep(self.sleep)
                continue
            try:
                self.client.login()
                self.client.check_all_attendance()
            except Exception as e:
                logging.error(e, exc_info=True)
            time.sleep(self.sleep)


banner = '''
           _        __                 _                 
          | |      / _|               (_)                
   ___  __| |_   _| |_ _ __  _ __ ___  _                 
  / _ \/ _` | | | |  _| '_ \| '_ ` _ \| |                
 |  __/ (_| | |_| | | | |_) | | | | | | |                
  \___|\__,_|\__,_|_| | .__/|_| |_| |_|_|  _             
             | |      | |             | | (_)            
   __ _ _   _| |_ ___ |_|__ ___   __ _| |_ _  ___  _ __  
  / _` | | | | __/ _ \| '_ ` _ \ / _` | __| |/ _ \| '_ \ 
 | (_| | |_| | || (_) | | | | | | (_| | |_| | (_) | | | |
  \__,_|\__,_|\__\___/|_| |_| |_|\__,_|\__|_|\___/|_| |_|
'''


def main():
    parser = argparse.ArgumentParser(description='Automate checking attendance')
    parser.add_argument('username')
    parser.add_argument('password')
    args = parser.parse_args()

    print(banner)

    ea = EdufpmiAutomator(args.username, args.password)
    ea.start()


if __name__ == '__main__':
    main()
