# 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim

# 设置环境变量，避免 Python 生成 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
# 设置环境变量，使 Python 输出直接到终端而不缓冲
ENV PYTHONUNBUFFERED 1

# 清空 sources.list
RUN echo "" > /etc/apt/sources.list

# 添加清华源 https://mirror.tuna.tsinghua.edu.cn/help/debian/
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-backports main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://security.debian.org/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list

# 更新软件源列表
RUN apt-get update
RUN apt-get upgrade -y

# 安装必要的软件包
RUN apt-get install -y libxinerama1
RUN apt-get install -y libcups2
RUN apt-get install -y libglib2.0-0
RUN apt-get install -y libcairo2
RUN apt-get install -y libsm6
RUN apt-get install -y libx11-xcb1
RUN apt-get install -y openjdk-17-jdk
RUN rm -rf /var/lib/apt/lists/*

# 创建软链接
RUN ln -s /opt/libreoffice7.1/program/soffice /usr/local/bin/libreoffice7.1

# 设置工作目录
WORKDIR /app

# 提前复制 requirements.txt 文件
COPY requirements.txt .

# 创建并激活虚拟环境，更新 pip 并安装依赖
RUN python -m venv venv && \
    . venv/bin/activate && \
    # 创建 pip 配置目录
    mkdir -p /root/.pip && \
    # 写入 pip 配置文件，设置镜像源
    echo "[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple\n[install]\ntrusted-host = pypi.tuna.tsinghua.edu.cn" > /root/.pip/pip.conf && \
    # 更新 pip
    pip install --upgrade pip && \
    # 安装项目依赖
    pip install -r requirements.txt

# 复制项目其他文件
COPY . .

# 暴露端口
EXPOSE 7005

# 启动服务，激活虚拟环境并运行服务
CMD ["/bin/bash", "-c", "source venv/bin/activate && python service.py"]