import TimeTree
import MailServer
import datetime
import os

server = os.environ['MAIL_SERVER']
user = os.environ['MAIL_SERVER_USER']
password = os.environ['MAIL_SERVER_PASS']

tt = TimeTree.TimeTree()
tt.setup_calendar()
ms = MailServer.MailServer(server)
ms.login(user, password)

estimates = ms.get_amazon_arriving_estimates()

for estimate_date, description in estimates:
    yaer = datetime.datetime.now().year
    if datetime.datetime.now().month == 12 and '01/' in estimate_date:
        # 12月中に届いた1月のお届予定は来年1月として処理
        yaer += 1
    estimate_date = datetime.datetime(year=yaer, month=int(estimate_date[0:2]), day=int(estimate_date[3:5]))

    tt.add_schedule('amazon来る', description, estimate_date)

ms.logout()
