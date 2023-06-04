import os
import time
# from dotenv import load_dotenv
import paramiko
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from env_params import EnvParams
import requests
# 如何加载.env 文件中的环境变量


# 设置电子邮件地址和要监视的网站URL
email_address = '1010602136@qq.com'
# 创建 EnvParams 类的实例
env_params = EnvParams()
# 调用 load_env() 方法，使得 env_vars 属性包含所有的环境变量
env_params.load_env()

env_params_data = env_params.env_vars
# 获得所有的环境变量
host_name = env_params_data['HOST_NAME']
username = env_params_data['USERNAME']
password = env_params_data['PASSWORD']
ssh_port = env_params_data['SSH_PORT']
qq_code = env_params_data['QQ_CODE']
# 使用 mian_domain 构建 website_url 变量
website_url = f'https://{host_name}/files/'
print(env_params_data)

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
    smtp_server.login(email_address, qq_code)  # 输入邮箱密码
    smtp_server.sendmail(email_address, email_address, message.as_string())
    smtp_server.quit()


def check_process():
    # 解包 vps_info 字典中的数据

    # SSH 连接相关设置
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接到远程服务器
        ssh.connect(hostname=host_name, username=username, password=password, port=ssh_port)

        # 检查进程是否正在运行
        stdin, stdout, stderr = ssh.exec_command(f'pgrep nginx')

        if stdout.read():
            print(f'在远程服务器{host_name}上正常运行着nginx')
        else:
            # 如果进程没有运行，则在服务器终端上启动它
            stdin, stdout, stderr = ssh.exec_command(
                '/usr/local/webserver/nginx/sbin/nginx -c /usr/local//webserver/nginx/conf/nginx.conf')
            print(f'请注意已经在远程服务器{host_name}上重新运行 ngixn 服务')
            send_email()


    except Exception as e:
        print(f'Error: {e}')

    finally:
        ssh.close()


def check_website():
    try:
        # 我需要这个 response 不含有缓存的内容,浏览器headers伪装
        headers = {
            'Cache-Control': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        response = requests.get(website_url, headers=headers)
        if response.status_code == 200:
            print(f'{website_url} 网站正在运行')
            return True
        else:
            print(f'请注意 {website_url} 网站已经挂了')
            send_email()
            return False
    except Exception as e:
        print(f'Error: {e}')


# 定义 vps_info 字典


while True:
    # 检查网站是否正在运行
    result = check_website()
    # 检查进程是否正在运行
    print("成功登陆网站，无需检查进程")
    if not result:
        check_process()
    # 每隔 10 分钟检查一次
    time.sleep(600)
