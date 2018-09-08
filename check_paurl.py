import sendemail
import requests, time
from datetime import timedelta
from lxml import html
import tldextract
import control_linux
from datetime import datetime
"""
cd E:\env\py3scrapy\Scripts
activate
cd E:\project\loganalyzer
python check_paurl.py
"""


link = "https://www.paurl.com"
sendemail.content = ''
sendemail.title = ''


def save_log(logtext):
    this_date_time = datetime.now().strftime("%Y-%m-%d %X")
    this_date = datetime.now().strftime("%Y-%m-%d")
    with open('./log/{}_weblog.txt'.format(this_date), 'a', encoding='utf-8') as f:
        f.write(logtext + " " + this_date_time + "\n")


def check_service(comm):
    service_result = control_linux.connected_linux(comm=comm)
    return service_result

def check_mysql(comm='systemctl status mysqld.service'):
    service_result = check_service(comm=comm)
    if 'running' in service_result:
        return True, service_result
    else:
        return False, service_result

def restart_mysql(comm='systemctl restart mysqld.service'):
    print("mysql服务挂了，正在重试....")
    save_log("mysql服务挂了，正在重试....")
    service_result, service_log = check_mysql(comm)

    if service_result:
        print("mysql重启成功，正在正常运行")
        save_log("mysql重启成功，正在正常运行")
        sendemail.title = link + "，" + "mysql重启成功，正在正常运行"
        sendemail.content = service_log
        sendemail.sendEmail()
        return True
    else:
        print("mysql重启失败，没有正常运行")
        save_log("mysql重启失败，没有正常运行")
        sendemail.title = link + "，" + "mysql重启失败，没有正常运行"
        sendemail.content = service_log
        sendemail.sendEmail()
        return False

def reboot_and_wdcp(comm='reboot'):
    print("尝试重启服务器....")
    save_log("尝试重启服务器....")
    check_service(comm=comm)
    time.sleep(30)

    print("正在开启wdcp服务....")
    save_log("正在开启wdcp服务....")
    check_service(comm="sh /www/wdlinux/wdcp/wdcp.sh start")
    time.sleep(3)

    if not check_mysql():
        print("重启服务器都不行，滚犊子了")
        save_log("重启服务器都不行，滚犊子了")
        sendemail.title = link + "重启服务器都不行，滚犊子了"
        sendemail.content = ""
        sendemail.sendEmail()
        return False
    else:
        return True

# 对网站发起请求，然后通过网站反馈的状态码判断是否正常执行
def check_website(l):
    try:
        res = requests.get(l, timeout=4)
        url = tldextract.extract(l)
        if res.status_code != 200:
            sendemail.content = "{}.{}发现以下问题：{}".format(url.domain, url.suffix, res.text)
            sendemail.title = "{}.{}访问异常了".format(url.domain, url.suffix)

            if not restart_mysql()[0]: reboot_and_wdcp()

        elif res.status_code == 200:
            sendemail.content = "{}.{}目前运行正常：{}".format(url.domain, url.suffix,
                                                        html.fromstring(res.content).xpath("//title/text()")[0])
            sendemail.title = "{}.{}目前运行正常".format(url.domain, url.suffix)
            print(sendemail.content)
            save_log(sendemail.content)
            sendemail.sendEmail()
    except Exception as e:
        print("check_website发生异常：{}".format(e))
        save_log("check_website发生异常：{}".format(e))
        time.sleep(10)
        check_website(l)

if __name__ == '__main__':

    sched_Timer = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, 0, 2) + \
                  timedelta(hours=1)
    while True:
        now_time = datetime.now()
        if now_time > sched_Timer:
            mysql_result = check_mysql()
            try:
                if mysql_result and now_time.minute == 0 and now_time.hour in [9, 14, 18, 22]:
                    check_website(link)
                elif mysql_result[0]:
                    print("目前mysql服务正常...")
                    save_log("目前mysql服务正常...")
                else:
                    # 重启mysql,如无效直接重启服务器
                    if not restart_mysql()[0]:
                        if not reboot_and_wdcp(): break
            except Exception as e:
                print("程序异常:{}".format(e))
                save_log("程序异常:{}".format(e))

                if not reboot_and_wdcp(): break
            else:
                sched_Timer += timedelta(minutes=1)
                if sched_Timer > now_time:
                    time.sleep((sched_Timer - now_time).seconds)
        else:
            time.sleep((sched_Timer - now_time).seconds)

