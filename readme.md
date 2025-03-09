## 构建镜像

cd /root/code/librefoffice
docker build -t libreoffice:1.0 -f Dockerfile .

## 运行镜像

docker run -d -p 7005:7005 --name libreoffice libreoffice:1.0

docker run -d -p 7005:7005 \
-v /opt/libreoffice7.1/program:/opt/libreoffice7.1/program \
-v /opt/libreoffice7.1/share:/opt/libreoffice7.1/share \
-v /root/code/librefoffice/office_data:/office_data \
--name libreoffice libreoffice:1.0

docker run -d -p 7005:7005 \
-v /opt/libreoffice7.1:/opt/libreoffice7.1 \
-e PATH=$PATH:/opt/libreoffice7.1/program \
--name libreoffice libreoffice:1.0

docker run -d -p 7005:7005 \
-v /opt/libreoffice7.1:/opt/libreoffice7.1 \
--name libreoffice libreoffice:1.0

## 查看运行状态

docker ps

## 查看日志

docker logs -f libreoffice

## 停止容器

docker stop libreoffice
docker rm -f libreoffice
docker image rm libreoffice:1.0

## 查看镜像

docker ps
docker ps -a

## 测试libreoffice

libreoffice7.1 --headless --convert-to docx --outdir /tmp/test_libreoffice /tmp/test_libreoffice/test.doc

## 进入容器

docker exec -it libreoffice bash