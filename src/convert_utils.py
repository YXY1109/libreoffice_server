import asyncio
import os
from typing import Tuple

from loguru import logger

# 定义支持的文件扩展名映射
SUPPORTED_EXTENSIONS = {".doc": ".docx", ".ppt": ".pptx", ".xls": ".xlsx"}


def get_target_extension(file_ext: str) -> str | None:
    """
    根据文件扩展名获取目标扩展名
    :param file_ext: 文件扩展名
    :return: 目标扩展名，如果不支持则返回 None
    """
    return SUPPORTED_EXTENSIONS.get(file_ext.lower())


async def run_conversion_command(command: str) -> Tuple[str | None, str | None]:
    """
    执行文件转换命令
    :param command: 要执行的命令
    :return: 命令执行结果，包含标准输出和标准错误信息
    """
    try:
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode()
    except Exception as e:
        logger.error(f"执行命令时出错: {e}")
        return None, None


async def convert_file_x(input_path: str, output_dir: str) -> str | None:
    logger.info(f"开始转换文件: {input_path}")
    # 获取文件名和扩展名
    file_name, file_ext = os.path.splitext(os.path.basename(input_path))
    # 获取目标文件扩展名
    target_ext = get_target_extension(file_ext)
    if not target_ext:
        logger.error(f"不支持的文件扩展名: {file_ext}")
        return None
    # 定义输出文件路径
    output_path = os.path.join(output_dir, file_name + target_ext)
    # 执行 LibreOffice 转换命令
    command = f"libreoffice7.1 --headless --convert-to {target_ext[1:]} --outdir {output_dir} {input_path}"
    logger.info(f"执行转换命令: {command}")
    stdout, stderr = await run_conversion_command(command)
    if stdout:
        logger.info(f"命令标准输出: {stdout}")
    if stderr:
        logger.error(f"命令标准错误: {stderr}")
    if os.path.exists(output_path):
        logger.info(f"文件转换成功: {output_path}")
        return output_path
    logger.error(f"文件转换失败: {input_path}")
    return None
