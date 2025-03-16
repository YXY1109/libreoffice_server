import asyncio
import os
from datetime import datetime

import aiofiles
from loguru import logger
from sanic import Sanic, response
from sanic.request import Request

from src.config import config
from src.convert_utils import convert_file_x
from src.minio_utils import upload_to_minio

# 定义文件大小限制常量
MAX_FILE_SIZE = 10 * 1024 * 1024

app = Sanic("Libreoffice_Service")


# 封装错误响应函数
def error_response(message, status):
    return response.json({'error': message}, status=status)


@app.before_server_start
async def server_start(app_s, loop):
    logger.info(f"server_start {__name__}")
    app_s.ctx.config = config


@app.before_server_stop
async def server_down(app_d, loop):
    logger.info(f"server_down {__name__}")


@app.route("/test", methods=["GET"])
async def test(request):
    # 获取当前年月日时分秒的时间
    formatted_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return response.json({"test": f"7我是libreoffice测试接口：{formatted_now}"}, status=200)


@app.route('/convert', methods=['POST'])
async def convert(request: Request):
    user_id = request.form.get("user_id", 1)
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return response.json({'error': '文件不存在'}, status=400)
    # 获取上传的文件
    file = request.files.get('file')
    file_name = file.name
    logger.info(f"文件名：{file_name}")
    file_size = len(file.body)
    logger.info(f"文件大小：{file_size}b")
    if file_size > MAX_FILE_SIZE:
        return error_response('文件大小超过10M的限制', 400)

    async with aiofiles.tempfile.TemporaryDirectory() as temp_dir:
        # 保存上传的文件到临时目录
        input_path = os.path.join(temp_dir, file_name)
        async with aiofiles.open(input_path, 'wb') as f:
            await f.write(file.body)
        # 执行文件转换
        output_path = await convert_file_x(input_path, temp_dir)
        # 上传到minio
        if output_path:
            file_url = await asyncio.to_thread(upload_to_minio, user_id, output_path)
            if file_url:
                return response.json({'file_urls': file_url}, status=200)
            else:
                return error_response('上传失败', 500)
        else:
            return error_response('转换失败，只支持doc、ppt、xls格式', 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7005)
