import requests

login_url = "http://47.93.230.103:7666/login"
server_url = "http://47.93.230.103:7666/sys/server"
restart_server = "http://47.93.230.103:7666/sys/server?act=restart&srv=mysqld"

headers = {
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate",
    "Accept-Language":"zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6",
    "Connection":"keep-alive",
    "Content-Length":"247",
    "Content-Type":"multipart/form-data; boundary=----WebKitFormBoundaryPghtbA2RGirNeAqp",
    "Host":"47.93.230.103:7666",
    "Origin":"http://47.93.230.103:7666",
    "Referer":"http://47.93.230.103:7666/login",
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "X-Requested-With":"XMLHttpRequest",
}
payload = """------WebKitFormBoundaryPghtbA2RGirNeAqp
Content-Disposition: form-data; name="username"

admin
------WebKitFormBoundaryPghtbA2RGirNeAqp
Content-Disposition: form-data; name="passwd"

Qq75992322
------WebKitFormBoundaryPghtbA2RGirNeAqp--
"""
def restart_mysql():
    session = requests.Session()
    session.post(login_url, files={'file':payload}, headers=headers)
    res = session.get(restart_server)
    return res.json()['msg']