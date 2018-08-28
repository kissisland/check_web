import paramiko
hostname = "47.93.230.103"
port = 22
username = "root"
password = "Qq75992322"

def connected_linux(comm, host=hostname, por=port, user=username, pawd=password):
    ssh = paramiko.SSHClient()
    # 設定自動加入 遠端主機的 SSH Key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 設定連接 ssh 的主機名稱, 使用者名稱, ssh 私鑰路徑
    #ssh.connect(hostname=REMOTEHOST, username=USERNAME, pkey=key)
    ssh.connect(hostname=host, port=por, username=user, password=pawd)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command=comm)

    if ssh_stdout:
        return " ".join(ssh_stdout.readlines())
    else:
        return "命令执行完毕..."

if __name__ == '__main__':

    returl = connected_linux(comm="systemctl status mysqld.service")
    print(returl)