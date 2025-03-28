from mimetypes import guess_type
import os

from loguru import logger
from minio import Minio

from src.config import config


def create_bucket_if_not_exists(client: Minio, bucket_name: str) -> None:
    """
    如果桶不存在，则创建桶
    :param client: Minio客户端
    :param bucket_name: 桶名称
    """
    try:
        bucket_exists = client.bucket_exists(bucket_name)
        logger.info(f"Bucket exists: {bucket_exists}")
        if bucket_exists:
            logger.info(f"桶 {bucket_name} 已存在")
        else:
            try:
                client.make_bucket(bucket_name=bucket_name)
                logger.info(f"创建桶：{bucket_name}，成功！")
            except Exception as e:
                logger.error(f"创建桶 {bucket_name} 失败: {e}")
    except Exception as e:
        logger.error(f"create bucket failed: {e}")


def upload_file(client: Minio, bucket_name: str, source_file: str) -> str | None:
    """
    上传单个文件到Minio
    :param client: Minio客户端
    :param bucket_name: 桶名称
    :param source_file: 源文件路径
    :return: 文件下载地址
    """
    destination_file = os.path.basename(source_file)
    content_type, _ = guess_type(source_file)

    try:
        # minio 的 put_object 方法目前不支持异步文件对象，所以使用 open 同步打开文件
        file_stat = os.stat(source_file)
        with open(source_file, "rb") as sync_file:
            client.put_object(bucket_name, destination_file, data=sync_file, length=file_stat.st_size)
        logger.success(f"File {destination_file} uploaded with content-type {content_type}.")
        file_url = client.presigned_get_object(bucket_name, destination_file)
        file_url = file_url.replace(" ", "%20")
        logger.info(f"文件下载地址：{file_url}")
        return file_url
    except Exception as e:
        logger.error(f"上传文件 {source_file} 失败: {e}")
        return None


def upload_to_minio(user_id: int, source_file_list: list[str] | str) -> list[str]:
    """
    上传文件到Minio
    :param user_id: 用户id
    :param source_file_list: 用户上传的文件
    :return:
    """
    client = Minio(
        endpoint=f"{config.MINIO_URL}",
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        secure=False,
    )
    logger.info(f"Minio客户端创建成功；{client}")

    bucket_name = f"libreoffice-{user_id}"
    logger.info(f"bucket_name: {bucket_name}")
    create_bucket_if_not_exists(client, bucket_name)

    if isinstance(source_file_list, str):
        source_file_list = [source_file_list]

    file_url_list = []
    for source_file in source_file_list:
        file_url = upload_file(client, bucket_name, source_file)
        if file_url:
            file_url_list.append(file_url)

    return file_url_list


if __name__ == "__main__":
    upload_to_minio(3, "/Users/cj/Downloads/test.doc")
