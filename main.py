import requests
import re
import time
import argparse
import logging

log_format = '%(asctime)s %(filename)s: %(message)s'
logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

parser = argparse.ArgumentParser(description='Automate checking attendance')
parser.add_argument('username')
parser.add_argument('password')
args = parser.parse_args()


class EdufpmiClient:
    LOGIN_URL = 'https://edufpmi.bsu.by/login/index.php'
    ALL_DAY_ATTENDANCE_URL = 'https://edufpmi.bsu.by/calendar/view.php?view=day'
    ATTENDANCE_URL = 'https://edufpmi.bsu.by/mod/attendance/attendance.php'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = None

    def login(self):
        request_data = {'username': self.username,
                        'password': self.password,
                        'referer': EdufpmiClient.LOGIN_URL}

        if self.session:
            self.session.close()

        self.session = requests.session()

        page = self.session.get(EdufpmiClient.LOGIN_URL).text
        token = re.search('logintoken".*value.*"(.*)"', page).group(1)
        request_data['logintoken'] = token

        logging.info(f'logging in with : username={self.username}, password={self.password}, csrf token: {token}')

        response = self.session.post(EdufpmiClient.LOGIN_URL, request_data)

        if 'loginerrors' in response.text:
            raise RuntimeError('Cannot log in. Please re-check your username and password')

    def get_attendance_urls(self):
        page = self.session.get(EdufpmiClient.ALL_DAY_ATTENDANCE_URL).text
        pattern = r'<a href="(https:\/\/edufpmi\.bsu\.by\/mod\/attendance\/view\.php\?id=\d+)" class="card-link">.*<\/a>'
        attendance_urls = re.findall(pattern, page)
        logging.info(f'successful get_attendance_urls: {attendance_urls}')
        return attendance_urls

        # except Exception:
        #     raise RuntimeError('get_attendance_url error: maybe you haven\'t log in')

    def get_attendance_form_data(self, attendance_page_url):
        page = self.session.get(attendance_page_url).text
        pattern = r'<td class="statuscol cell c2 lastcol" style="text-align:center;width:\*;" colspan="3">' \
                  r'<a href="https:\/\/edufpmi\.bsu\.by\/mod\/attendance\/attendance\.php\?' \
                  r'sessid=(\d+)&amp;sesskey=(.+)">Submit attendance<\/a><\/td>'
        return re.findall(pattern, page)

    def get_all_attendance_form_data(self):
        all_forms = list()
        for url in self.get_attendance_urls():
            all_forms += self.get_attendance_form_data(url)
        logging.info(f'all forms data: {all_forms}')
        return all_forms

    def post_attendance(self, session_id, session_key):

        page_url = f'{EdufpmiClient.ATTENDANCE_URL}?sessid={session_id}&sesskey={session_key}'

        form_page = self.session.get(page_url).text
        pattern = r'<input.+?form-check-input.+?value="(.+?)".*?>'
        radiobutton = re.findall(pattern, form_page, re.DOTALL)[0]

        logging.info(f'radiobutton: {radiobutton}')

        form_data = {'sessid': session_id,
                     'sesskey': session_key,
                     '_qf__mod_attendance_student_attendance_form': 1,
                     'mform_isexpanded_id_session': 1,
                     'status': radiobutton,
                     'submitbutton': 'Save changes'}

        response = self.session.post(
            EdufpmiClient.ATTENDANCE_URL, data=form_data)
        logging.info(f'check_attendance: code={response.status_code}')

    def check_all_attendance(self):
        all_form_data = self.get_all_attendance_form_data()
        for fd in all_form_data:
            self.post_attendance(*fd)


class EdufpmiAutomator:
    def __init__(self, username, password, sleep=60 * 20):
        self.client = EdufpmiClient(username, password)
        self.sleep = sleep

    def start(self):

        while True:
            try:
                print('-'*40)
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
    print(banner)
    ea = EdufpmiAutomator(args.username, args.password)
    ea.start()


if __name__ == '__main__':
    main()
