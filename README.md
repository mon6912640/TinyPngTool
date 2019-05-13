# TinyPngTool
基于python的tinypng图片压缩工具（在线压缩）

## 功能特性
> 1.调用tinypng的API进行在线图片压缩  
> 2.支持命令行调用  
> 3.内建本地缓存数据库，已经压缩过的图片会在本地缓存起来，如果检测有缓存，则直接从缓存取出来，免去了网络压缩的流程和重复图片压缩的时间  

## 使用方法
```cmd
python TinyPngTool.py --source your_source_dir --output your_output_dir
```

```yaml
参数说明：
--source 需要压缩的图片源目录
--output 压缩后图片输出的目录
```

> TinyPng开发者key申请地址  
> https://tinypng.com/developers


## 参考
代码参考自以下库  
https://github.com/fengqingxiuyi/LearningNotes

## 更多
一个基于Electron开发的优秀图片压缩工具（可离线使用）  
https://github.com/meowtec/Imagine
