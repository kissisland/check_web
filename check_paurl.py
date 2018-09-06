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

# 对网站发起请求，然后通过网站反馈的状态码判断是否正常执行
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


def check_service(comm):
    service_result = conn_linux.connected_linux(comm=comm)
    return service_result

def check_mysql(comm='systemctl status mysqld.service'):
    service_result = check_service(comm=comm)
    if 'running' in service_result:
        return True
    else:
        return False

def restart_mysql(comm='systemctl restart mysqld.service'):
    service_result = check_mysql()
    if not service_result:
        check_service(comm)

    if check_mysql():
        print("mysql重启成功，正在正常运行")
        save_log("mysql重启成功，正在正常运行")
        return True
    else:
        print("mysql重启失败，没有正常运行")
        save_log("mysql重启失败，没有正常运行")
        return False

def reboot_and_wdcp(comm='reboot'):
    print("尝试重启服务器....")
    save_log("尝试重启服务器....")
    check_service(comm=comm)
    time.sleep(30)

    print("正在开启wdcp服务....")
    save_log("正在开启wdcp服务....")
    check_service(comm="sh /www/wdlinux/wdcp/wdcp.sh start")


if __name__ == '__main__':
    sched_Timer = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, 0, 2) + \
                  timedelta(hours=1)
    retries = True
    while True:
        now_time = datetime.now()
        if now_time > sched_Timer:
            mysql_result = check_mysql()

            try:
                if mysql_result and now_time.minute == 0 and now_time.hour in [9, 14, 18, 22]:
                    if check_website(link):
                        print(sendemail.content)
                        save_log(sendemail.content)
                        retries = True
                        sendemail.sendEmail()
                elif mysql_result:
                    retries = True
                    print("目前mysql服务正常...")
                    save_log("目前mysql服务正常...")
                else:

                    if retries:
                        # 重启mysql,如无效直接重启服务器
                        if not restart_mysql():
                            reboot_and_wdcp()
                            sendemail.title += "，重启mysql失败，重启服务器成功"
                        else:
                            sendemail.title += "，自动重启mysql成功"
                        retries = False
                        sendemail.sendEmail()
                    else:
                        print("重启服务器都不行，滚犊子了")
                        save_log("重启服务器都不行，滚犊子了")
                        sendemail.title = link + "重启服务器都不行，滚犊子了"
                        sendemail.sendEmail()
                        break
            except Exception as e:
                print("程序异常:{}".format(e))
                save_log("程序异常:{}".format(e))
                sendemail.title = "程序异常了," + sendemail.title
                sendemail.content = sendemail.content + "，{}".format(e)
                sendemail.sendEmail()
                reboot_and_wdcp()
            else:
                sched_Timer += timedelta(minutes=1)
                time.sleep((sched_Timer - now_time).seconds)
        else:
            time.sleep((sched_Timer - now_time).seconds)

