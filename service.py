import asyncio
import os
import shutil
import tempfile
from datetime import datetime

import aiofiles
from loguru import logger
from sanic import Sanic, response
from sanic.request import Request

app = Sanic(__name__)


async def convert_file_async(input_path, output_dir):
    logger.info(f"开始转换文件: {input_path}")
    # 获取文件名和扩展名
    file_name, file_ext = os.path.splitext(os.path.basename(input_path))
    # 定义目标文件扩展名
    target_ext = {
        '.doc': '.docx',
        '.ppt': '.pptx',
        '.xls': '.xlsx'
    }.get(file_ext.lower())
    if not target_ext:
        logger.error(f"不支持的文件扩展名: {file_ext}")
        return None
    # 定义输出文件路径
    output_path = os.path.join(output_dir, file_name + target_ext)
    # 执行 LibreOffice 转换命令
    command = f'libreoffice7.1 --headless --convert-to {target_ext[1:]} --outdir {output_dir} {input_path}'
    logger.info(f"执行转换命令: {command}")
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
    await process.communicate()
    if os.path.exists(output_path):
        logger.info(f"文件转换成功: {output_path}")
        return output_path
    logger.error(f"文件转换失败: {input_path}")
    return None


@app.route('/convert', methods=['POST'])
async def convert(request: Request):
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return response.json({'error': '文件不存在'}, status=400)
    # 获取上传的文件
    file = request.files.get('file')
    file_name = file.name
    logger.info(f"文件名：{file_name}")
    file_size = len(file.body)
    logger.info(f"文件大小：{file_size}b")
    if file_size > 10 * 1024 * 1024:
        return response.json({'error': '文件大小超过10M的限制'}, status=400)
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        # 保存上传的文件到临时目录
        input_path = os.path.join(temp_dir, file.name)
        async with aiofiles.open(input_path, 'wb') as f:
            await f.write(file.body)
        # 执行文件转换
        output_path = await convert_file_async(input_path, temp_dir)
        if output_path:
            # 读取转换后的文件内容
            async with aiofiles.open(output_path, 'rb') as f:
                file_content = await f.read()
            # 返回转换后的文件
            return response.raw(
                file_content,
                headers={
                    'Content-Disposition': f'attachment; filename={os.path.basename(output_path)}'
                }
            )
        else:
            return response.json({'error': '转换失败，只支持doc、ppt、xls格式'}, status=500)
    except Exception as e:
        return response.json({'error': f"转换异常：{str(e)}"}, status=500)
    finally:
        # 删除临时目录
        shutil.rmtree(temp_dir)


@app.route("/test", methods=["GET"])
async def test(request):
    # 获取当前年月日时分秒的时间
    formatted_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return response.json({"test": f"3我是libreoffice测试接口：{formatted_now}"}, status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7005)
