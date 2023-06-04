import os
import time
#from dotenv import load_dotenv
import paramiko
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests

# 设置电子邮件地址和要监视的网站URL
email_address = '1010602136@qq.com'
# load_dotenv() 会从 .env 文件中读取环境变量，如果希望从其他文件中读取环境变量，可以使用 load_dotenv(dotenv_path='path/to/.env')
#load_dotenv()

# 脚本变量和环境变量关联起来
host_name = os.environ.get('HOST_NAME')
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
ssh_port = os.environ.get('SSH_PORT')

# 使用 mian_domain 构建 website_url 变量
website_url = f'https://{host_name}/files/'
vps_info = {
    'hostname':host_name,
    'username': username,
    'password': password,
    'ssh_port': ssh_port,
    'process_name': 'nginx'
}

def send_email():
    # 邮件内容
    message = MIMEMultipart()
    message['Subject'] = f'{website_url} 这个网站挂了'
    message['From'] = email_address
    message['To'] = email_address

    text = MIMEText(f'{website_url} 这个网站挂了，快去看看！，我应该重新部署上线了，但是建议你还是检查一下')
    message.attach(text)

    # 调用SMTP服务器发送邮件
    smtp_server = smtplib.SMTP('smtp.qq.com', 587)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.login(email_address, 'auujifpmshbpbcge') # 输入邮箱密码
    smtp_server.sendmail(email_address, email_address, message.as_string())
    smtp_server.quit()


def check_process(vps_info):
    # 解包 vps_info 字典中的数据
    hostname = vps_info['hostname']
    username = vps_info['username']
    password = vps_info['password']
    ssh_port = vps_info['ssh_port']
    process_name = vps_info['process_name']

    # SSH 连接相关设置
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接到远程服务器
        ssh.connect(hostname=hostname, username=username, password=password, port=ssh_port)

        # 检查进程是否正在运行
        stdin, stdout, stderr = ssh.exec_command(f'pgrep {process_name}')

        if stdout.read():
            print(f'在远程服务器{hostname}上正常运行着{process_name}')
        else:
            # 如果进程没有运行，则在服务器终端上启动它
            stdin, stdout, stderr = ssh.exec_command(
                '/usr/local/webserver/nginx/sbin/nginx -c /usr/local//webserver/nginx/conf/nginx.conf')
            print(f'请注意已经在远程服务器{host_name}上重新运行 {process_name}服务')
            send_email()


    except Exception as e:
        print(f'Error: {e}')

    finally:
        ssh.close()

def check_website(website_url):
    try:
        # 我需要这个 response 不含有缓存的内容
        response = requests.get(website_url, headers={'Cache-Control': 'no-cache'})
        if response.status_code == 200:
            print(f'{website_url} 网站正在运行')
        else:
            print(f'请注意 {website_url} 网站已经挂了')
            send_email()

    except Exception as e:
        print(f'Error: {e}')

# 定义 vps_info 字典


while True:
# 检查进程是否正在运行
    check_process(vps_info)

    # 每隔 10 分钟检查一次
    time.sleep(600)



