"""
tinypng的http实现
"""
import base64
from pathlib import Path

import requests

from errors import *

source = ''
output = ''
key = ''


def compress(p_source, p_output):
    source = p_source
    output = p_output
    if not source:
        raise Error.create('不存在源文件', '参数错误', 'unkonwn')
    if not output:
        raise Error.create('没有指定输出路径', '参数错误', 'unkonwn')
    if not key:
        raise Error.create('没有指定api key', '参数错误', 'unkonwn')
    path_source = Path(source)
    img_bytes = path_source.read_bytes()
    key_prefix = 'api:'
    raw_key = (key_prefix + key).encode('ascii')
    encode_key = base64.standard_b64encode(raw_key).decode('ascii')

    header = {'Authorization': 'Basic ' + encode_key}
    try:
        # 上传图片 POST
        r_post = requests.post('https://api.tinify.com/shrink', headers=header, data=img_bytes)
    except Exception as err:
        # 捕获异常
        raise Error.create('连接异常 {0}'.format(err), 'post error', 'unkonwn')
    else:
        pass

    if r_post.ok:  # 成功返回
        # 下载压缩后的图片 GET
        result = requests.get(r_post.headers.get('location'), headers=header)
        path_output = Path(output)
        path_output.parent.mkdir(parents=True, exist_ok=True)
        with open(str(path_output), 'wb') as f:
            f.write(result.content)
    else:  # 不成功返回
        try:
            details = r_post.json()
        except Exception as err:
            details = {'message': 'HTTP code:{0} Error while parsing response: {1}'.format(r_post.status_code, err),
                       'error': 'ParseError'}
        raise Error.create(details.get('message'), details.get('error'), r_post.status_code)
