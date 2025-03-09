## 构建镜像

cd /root/code/librefoffice
docker build -t libreoffice:1.0 -f Dockerfile .

## 运行镜像

```
#docker
docker run -d -p 7005:7005 \
-v /opt/libreoffice7.1:/opt/libreoffice7.1 \
--name libreoffice libreoffice:1.0

#docker-compose
docker-compose up -d

# 查看运行状态
docker ps

# 查看日志
docker logs -f libreoffice

# 进入容器
docker exec -it libreoffice bash

# 停止容器
docker stop libreoffice
docker rm -f libreoffice
docker image rm libreoffice:1.0

# 测试libreoffice
libreoffice7.1 --headless --convert-to docx --outdir /tmp/test_libreoffice /tmp/test_libreoffice/test.doc
```