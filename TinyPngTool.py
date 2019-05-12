# -*- coding:utf-8 -*-

# 说明
## 1. Developer API Key地址：进入https://tinypng.com/dashboard/developers网址后选择Developer API选项卡
## 2. API地址：https://tinypng.com/developers/reference/python
## 3. 免费用户每个月最多只能压500次，可通过多注册几个邮箱的方式解决次数的限制
import os.path
import time
import argparse

import tinify

fromPath = "./source"  # source dir path
toPath = "./compress"  # compress dir path

# 压缩图片的key
online_key_list = [
    'G2oCafKlhjcHoHQokyvnkz6Rn6LoOlOl',
    "RdHoRF9i936xXJCP-ES2c9YCHB0MhxOh",
    "q20BBKkn5t6_AZBxYL1sJcLiW0a4Cufq",  # 可以继续添加  防止一个key不够
]
online_key_list_iter = iter(online_key_list)
online_key = next(online_key_list_iter)


# 在线压缩
def compress_online(source_path, output_path):
    global online_key
    compress_key = online_key

    tinify.key = compress_key
    print('上传压缩图片...' + source_path, end=' ')
    result = False
    try:
        source = tinify.from_file(source_path)
        source.to_file(output_path)
    except tinify.AccountError as e:
        # Verify your API key and account limit.
        # 如果key值无效 换一个key继续压缩
        print("key值无效 换一个继续。。。")
        online_key = next(online_key_list_iter)
        compress_online(source_path, output_path)  # 递归方法 继续读取
        result = True
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
        compress_online(source_path, output_path)  # 递归方法 继续读取
        result = True
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='帮助信息')
    parser.add_argument('--source', type=str, default=fromPath, help='需要压缩的源目录')
    parser.add_argument('--output', type=str, default=toPath, help='输出的目录')
    args = parser.parse_args()

    print('source_path = '+args.source)
    print('output_path = '+args.output)
    fromPath = args.source
    toPath = args.output

    if not os.path.exists(fromPath):
        print('源目录不存在，程序退出')
        exit()

    for root, dirs, files in os.walk(fromPath):
        newToPath = toPath
        from_abs_path = os.path.abspath(fromPath)
        to_abs_path = os.path.abspath(toPath)

        for file_name in files:
            source_path = os.path.abspath(os.path.join(root, file_name))
            rel_path = os.path.relpath(source_path, from_abs_path)
            target_path = os.path.join(to_abs_path, rel_path)
            fileName, fileSuffix = os.path.splitext(file_name)  # 分解文件名的扩展名
            if fileSuffix == '.png' or fileSuffix == '.jpg':
                # 在线压缩
                parent_dir = os.path.dirname(target_path)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
                if not compress_online(source_path, target_path):
                    print("压缩失败，检查报错信息")
                    exit()
                pass
            else:
                pass
