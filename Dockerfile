FROM python:3.9-slim-buster

# 设置环境变量，如何设置默认环境变量
ENV HOST_NAME=""
ENV USERNAME="root"
ENV PASSWORD=""
ENV SSH_PORT="29271"




# 复制 main.py 文件到容器中
COPY main.py /
COPY requirements.txt /
# 安装需要的库
RUN pip3 install --no-cache-dir -r /requirements.txt

# 设置启动命令
CMD ["python", "main.py"]