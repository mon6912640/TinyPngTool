# -*- coding:utf-8 -*-

import argparse
import hashlib
import json
import os.path
import shutil
import socket
import sqlite3
import time
from pathlib import Path, PurePath

import socks
import tinify

from_path = "./source"  # source dir path
to_path = "./compress"  # compress dir path
cache_path = './cache'
proxy = ''
# 数据库打开标识
db_open = False

# 压缩图片的key
online_key_list = [
    'G2oCafKlhjcHoHQokyvnkz6Rn6LoOlOl',
    "RdHoRF9i936xXJCP-ES2c9YCHB0MhxOh",
    "q20BBKkn5t6_AZBxYL1sJcLiW0a4Cufq",  # 可以继续添加  防止一个key不够
]

# 加载外部配置
with open('./config.json', 'r', encoding='utf-8') as f:
    config = json.loads(f.read())
    online_key_list = config['keys']
    if 'sourcePath' in config:
        from_path = config['sourcePath']
    if 'outputPath' in config:
        to_path = config['outputPath']
    if 'proxy' in config:
        proxy = config['proxy']

if proxy:
    """
    使用socks5代理
    """
    socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', 1080)
    socket.socket = socks.socksocket

online_key_list_iter = iter(online_key_list)
online_key = next(online_key_list_iter)


# 在线压缩
def compress_online(source_path, output_path):
    global online_key
    compress_key = online_key

    tinify.key = compress_key
    # if proxy:
    #     tinify.proxy = proxy
    print('上传压缩图片...' + source_path, end=' ')
    result = False
    try:
        source = tinify.from_file(source_path)
        source.to_file(output_path)
    except tinify.AccountError as e:
        # Verify your API key and account limit.
        # 如果key值无效 换一个key继续压缩
        print("key值无效 换一个继续。。。")
        try:
            online_key = next(online_key_list_iter)
        except:
            print('配置的key已经用完了，请到官网申请更多的key https://tinypng.com/developers')
            result = False
        else:
            result = compress_online(source_path, output_path)  # 递归方法 继续读取
    except tinify.ClientError as e:
        # Check your source image and request options.
        print("Check your source image and request options. %s" % e.message)
        result = False
    except tinify.ServerError as e:
        # Temporary issue with the Tinify API.
        print("Temporary issue with the Tinify API. %s" % e.message)
        result = False
    except tinify.ConnectionError as e:
        # A network connection error occurred.
        print("网络故障。。。休息1秒继续")
        time.sleep(1)
        result = compress_online(source_path, output_path)  # 递归方法 继续读取
    except Exception as e:
        # Something else went wrong, unrelated to the Tinify API.
        print("Something else went wrong, unrelated to the Tinify API.  %s" % e.message)
        result = False
    else:
        if os.path.exists(source_path) and os.path.exists(output_path):
            source_size = os.path.getsize(source_path)
            output_size = os.path.getsize(output_path)
            ratio_reduce = int((output_size - source_size) / source_size * 100)
            print('√ ' + str(ratio_reduce) + '%')
        result = True
    return result


def cal_md5(file_path) -> str:
    with open(file_path, 'rb') as f:
        hash = hashlib.md5()
        while 1:
            b = f.read(128)
            if not b:
                break
            hash.update(b)
    md5_str = hash.hexdigest()
    return md5_str


def create_db():
    # 创建表名为md5的数据库表
    global db_open
    if db_open:
        return
    global conn
    conn = sqlite3.connect('map.db')
    global cr
    cr = conn.cursor()
    # 建表需要判断数据表是否存在 if not exists
    cr.execute('create table if not exists `md5` (id text primary key, md5_value text)')
    db_open = True


def close_db():
    # commit并关闭数据库，保存之前已经正确处理的数据
    global db_open
    if not db_open:
        return
    conn.commit()
    cr.close()
    conn.close()
    db_open = False


def handle_file(source_path, target_path):
    # target_path = Path(target_path)
    # source_path = Path(source_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    source_md5 = cal_md5(source_path)
    key_str = source_md5

    need_upload = False
    is_in_db = False
    cr.execute('select * from md5 where id=?', (key_str,))
    values = cr.fetchone()
    if values is None:  # 数据库不存在，则需要上传压缩图片
        cr.execute('select md5_value from `md5` where md5_value=?', (key_str,))
        if cr.fetchone() is not None:  # 主键不存在但存在于压缩值中，则表示这个图片是已经压缩过了，无需做处理
            cache_file = os.path.join(cache_path, key_str + target_path.suffix)
            if not os.path.exists(cache_file):  # 如果没有缓存文件，则复制一份到缓存目录以备后用
                shutil.copyfile(source_path, cache_file)
            shutil.copyfile(source_path, target_path)  # 不做处理，直接复制到目标目录
            print(str(source_path) + ' 已经压缩过了，不做处理')
            pass
        else:
            need_upload = True
    else:  # 数据库存在
        is_in_db = True
        output_md5 = values[1]
        cache_file = os.path.join(cache_path, output_md5 + target_path.suffix)
        if os.path.exists(cache_file):  # 存在缓存文件，则从缓存文件夹复制出来
            # 从缓存目录取出来并复制到目标目录
            shutil.copyfile(cache_file, target_path)
            print(str(source_path) + ' 从缓存取出')
            pass
        else:  # 不存在缓存文件，则上传压缩图片
            need_upload = True
            print(str(source_path) + ' 数据库存在，但没有缓存')
            pass

    if need_upload:
        if not compress_online(str(source_path), str(target_path)):
            print("压缩失败，检查报错信息")
            close_db()
            return False
        else:
            # 上传压缩成功并下载压缩文件回来了
            output_md5 = cal_md5(target_path)
            cache_file = os.path.join(cache_path, output_md5 + target_path.suffix)
            shutil.copyfile(target_path, cache_file)  # 复制一份文件到缓存目录

            if is_in_db:
                # 原来数据库有记录，则更新数据库
                cr.execute('update md5 set md5_value=? where id=?', (output_md5, source_md5))
                pass
            else:
                # 数据库没有记录，这插入新数据
                cr.execute('insert into md5 (id, md5_value) values(?,?)', (source_md5, output_md5))
                pass
    return True


def run(p_source_path, p_output_path):
    path_source = Path(p_source_path)
    path_output = Path(p_output_path)

    if path_output.exists() and not path_output.is_dir():
        print('指定的输出路径不是一个目录，程序退出')
        return

    path_output.mkdir(parents=True, exist_ok=True)

    if not path_source.exists():
        print('源目录/文件不存在，程序退出')
        return

    file_count = 0
    start = time.time()

    # 创建缓存目录
    path_cache = Path(cache_path)
    path_cache.mkdir(parents=True, exist_ok=True)

    create_db()  # 创建数据库

    if path_source.is_file():
        path_target = path_output / path_source.name
        if handle_file(path_source, path_target):
            file_count += 1
        pass
    elif path_source.is_dir():
        list_file = sorted(path_source.rglob('*.*'))
        for v in list_file:
            if v.suffix == '.png' or v.suffix == '.jpg':
                path_rel = v.relative_to(path_source)
                path_target = path_output / path_source.name / path_rel
                if handle_file(v, path_target):
                    file_count += 1
        pass

    end = time.time()
    print('输出 %s 个文件' % file_count)
    print('总用时', end - start)

    # 数据库需要commit之后才会真正写进文件，不然不会生效
    close_db()


def run_by_list(p_list, p_output_path):
    for v in p_list:
        run(v, p_output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='帮助信息')
    parser.add_argument('--source', type=str, default=from_path, help='需要压缩的源目录')
    parser.add_argument('--output', type=str, default=to_path, help='输出的目录')
    args = parser.parse_args()

    print('source_path = ' + args.source)
    print('output_path = ' + args.output)
    run_by_list(args.source.split(','), args.output)
    # run(args.source, args.output)
