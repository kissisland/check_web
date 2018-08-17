import sendemail
import requests, time
from datetime import datetime,timedelta
from lxml import html
import tldextract

"""
cd E:\env\py3scrapy\Scripts
activate
cd E:\project\loganalyzer
python check_paurl.py
"""
"""原代码"""

# sched_Timer=datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour + 1, 0, 2)
# flag = True
# while True:
#     now_time = datetime.now()
#     if now_time > sched_Timer:
#         res = requests.get("http://www.paurl.com")
#         if res.status_code != 200:
#             sendemail.content = "{}发现以下问题：{}".format(res.url, res.text)
#             sendemail.title = "paurl.com访问异常了"
#             sendemail.sendEmail()
#         elif now_time.hour in [9, 18, 14, 22] and res.status_code == 200 and flag:
#         # elif res.status_code == 200:
#             sendemail.content = "paurl.com目前运行正常：{}".format(html.fromstring(res.content).xpath("//title/text()")[0])
#             sendemail.title = "paurl.com目前运行正常"
#             sendemail.sendEmail()
#             flag = False
#
#         sched_Timer += timedelta(minutes=15)
#
#         if sched_Timer.hour > now_time.hour:
#             flag = True
#
#         time.sleep(840)
link = "https://www.paurl.com"
sendemail.content = ''
sendemail.title = ''
def check_website(l):
    try:
        res = requests.get(l)
        url = tldextract.extract(l)
        if res.status_code != 200:
            sendemail.content = "{}.{}发现以下问题：{}".format(url.domain,url.suffix, res.text)
            sendemail.title = "{}.{}访问异常了".format(url.domain,url.suffix)
            return False
        elif res.status_code == 200:
            sendemail.content = "{}.{}目前运行正常：{}".format(url.domain,url.suffix,
                                                        html.fromstring(res.content).xpath("//title/text()")[0])
            sendemail.title = "{}.{}目前运行正常".format(url.domain,url.suffix)
            return True
    except Exception as e:
        print("check_website发生异常：{}".format(e))
        time.sleep(10)
        return check_website(l)
if __name__ == '__main__':
    sched_Timer = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, 0, 2) + \
                  timedelta(hours=1)
    while True:
        now_time = datetime.now()
        if now_time > sched_Timer:
            result = check_website(link)

            if result and now_time.minute == 0 and now_time.hour in [9, 14, 18, 22]:
                print(sendemail.content)
                sendemail.sendEmail()
            elif result:
                print(sendemail.content)
            else:
                sendemail.sendEmail()
                print(sendemail.content)
            sched_Timer += timedelta(minutes=15)
            time.sleep((sched_Timer - now_time).seconds)
        else:
            time.sleep((sched_Timer - now_time).seconds)


