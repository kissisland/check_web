import sendemail
import requests, time
from datetime import datetime,timedelta
from lxml import html
import tldextract
import conn_linux
from datetime import datetime

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


def save_log(logtext):
    this_date_time = datetime.now().strftime("%Y-%m-%d %X")
    this_date = datetime.now().strftime("%Y-%m-%d")
    with open('./log/{}_weblog.txt'.format(this_date), 'a', encoding='utf-8') as f:
        f.write(logtext + " " + this_date_time + "\n")

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
        save_log("check_website发生异常：{}".format(e))
        time.sleep(10)
        return check_website(l)

if __name__ == '__main__':
    sched_Timer = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, 0, 2) + \
                  timedelta(hours=1)
    retries = True
    while True:
        now_time = datetime.now()
        if now_time > sched_Timer:
            result = check_website(link)
            try:
                if result and now_time.minute == 0 and now_time.hour in [9, 14, 18, 22]:
                    print(sendemail.content)
                    save_log(sendemail.content)
                    retries = True
                    sendemail.sendEmail()
                    save_log("邮件发送成功...")

                elif result:
                    retries = True
                    print(sendemail.content)
                    save_log(sendemail.content)
                else:

                    if retries:
                        sendemail.title += "，自动重启mysql"

                        # 查看mysqld的状态，从而优化直接访问网站得知进程挂掉的问题
                        mysqld_status = conn_linux.connected_linux(comm="systemctl status mysqld.service")
                        sendemail.content = mysqld_status
                        print(mysqld_status)
                        save_log(mysqld_status)

                        # 远程ssh重启mysql服务器
                        conn_linux.connected_linux("service mysqld restart")

                        retries = False

                        print(sendemail.title, "正在重启mysql....")
                        save_log(sendemail.title + "正在重启mysql....")
                    else:
                        sendemail.title += "，重启mysql无效，重启服务器中"

                        # 查看mysqld的状态，从而优化直接访问网站得知进程挂掉的问题
                        mysqld_status = conn_linux.connected_linux(comm="systemctl status mysqld.service")
                        sendemail.content = mysqld_status
                        print(mysqld_status)
                        save_log(mysqld_status)

                        print("正在重启服务器....")
                        save_log("正在重启服务器....")
                        conn_linux.connected_linux("reboot")
                        time.sleep(30)
                        print("正在开启wdcp服务....")
                        save_log("正在开启wdcp服务....")
                        conn_linux.connected_linux("sh /www/wdlinux/wdcp/wdcp.sh start")

                        retries = True
                    sendemail.sendEmail()
                    save_log("邮件发送成功")

            except Exception as e:
                print("程序异常:{}".format(e))
                save_log("程序异常:{}".format(e))

                sendemail.title = "程序异常了," + sendemail.title
                sendemail.content = sendemail.content + "，{}".format(e)
                sendemail.sendEmail()

                print("正在重启服务器....")
                save_log("正在重启服务器....")
                conn_linux.connected_linux("reboot")
                time.sleep(30)
                print("正在开启wdcp服务....")
                save_log("正在开启wdcp服务....")
                conn_linux.connected_linux("sh /www/wdlinux/wdcp/wdcp.sh start")
            else:

                sched_Timer += timedelta(minutes=3)
                time.sleep((sched_Timer - now_time).seconds)
        else:
            time.sleep((sched_Timer - now_time).seconds)

