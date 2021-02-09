import requests
import re
import time


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

        # try:
        page = self.session.get(EdufpmiClient.LOGIN_URL).text
        token = re.search('logintoken".*value.*"(.*)"', page).group(1)
        request_data['logintoken'] = token

        print(f'login: username={self.username}, password={self.password}')
        print(f'token: {token}')

        response = self.session.post(EdufpmiClient.LOGIN_URL, request_data)

        if response.status_code == 200:
            print('successful login')
        else:
            raise RuntimeError('error while login: non 200 code')

        # except Exception:
        #     raise RuntimeError('login error: check your username/password')

    def get_attendance_urls(self):
        # try:
        page = self.session.get(EdufpmiClient.ALL_DAY_ATTENDANCE_URL).text
        pattern = r'<a href="(https:\/\/edufpmi\.bsu\.by\/mod\/attendance\/view\.php\?id=\d+)" class="card-link">.*<\/a>'
        attendance_urls = re.findall(pattern, page)
        print('successful get_attendance_urls:', attendance_urls)
        return attendance_urls

        # except Exception:
        #     raise RuntimeError('get_attendance_url error: maybe you haven\'t log in')

    def get_attendance_form_data(self, attendance_page_url):
        page = self.session.get(attendance_page_url).text

        pattern = r'<td class="statuscol cell c2 lastcol" style="text-align:center;width:\*;" colspan="3"><a href="https:\/\/edufpmi\.bsu\.by\/mod\/attendance\/attendance\.php\?sessid=(\d+)&amp;sesskey=(.+)">Submit attendance<\/a><\/td>'

        return re.findall(pattern, page)

    def get_all_attendance_form_data(self):
        all_forms = list()
        for url in self.get_attendance_urls():
            all_forms += self.get_attendance_form_data(url)
        print('all forms data: ', all_forms)
        return all_forms

    def post_attendance(self, session_id, session_key):
        form_data = {'sessid': session_id,
                     'sesskey': session_key,
                     '_qf__mod_attendance_student_attendance_form': 1,
                     'mform_isexpanded_id_session': 1,
                     'status': 200,
                     'submitbutton': 'Save changes'}

        headers = {
            'referer': f'{EdufpmiClient.ATTENDANCE_URL}?sessid={session_id}&sesskey={session_key}'
        }

        response = self.session.post(EdufpmiClient.ATTENDANCE_URL, data=form_data, headers=headers)
        print(f'check_attendance: code={response.status_code}')

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
                print('---------------')
                self.client.login()
                self.client.check_all_attendance()
            except Exception as e:
                print(e)
            time.sleep(self.sleep)


banner = (
    '''
███████╗██████╗ ██╗   ██╗███████╗██████╗ ███╗   ███╗██╗                              
██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗████╗ ████║██║                              
█████╗  ██║  ██║██║   ██║█████╗  ██████╔╝██╔████╔██║██║                              
██╔══╝  ██║  ██║██║   ██║██╔══╝  ██╔═══╝ ██║╚██╔╝██║██║                              
███████╗██████╔╝╚██████╔╝██║     ██║     ██║ ╚═╝ ██║██║                              
╚══════╝╚═════╝  ╚═════╝ ╚═╝     ╚═╝     ╚═╝     ╚═╝╚═╝                              
                                                                                     
 █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ███╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
███████║██║   ██║   ██║   ██║   ██║██╔████╔██║███████║   ██║   ██║██║   ██║██╔██╗ ██║
██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══
    ''')


def main():
    print(banner)
    ea = EdufpmiAutomator(username='', password='')
    ea.start()


if __name__ == '__main__':
    main()
