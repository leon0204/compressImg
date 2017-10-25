#!/usr/bin/env python3
# coding=utf-8

import os,sys, getopt
from urllib.request import Request, urlopen
from base64 import b64encode
from multiprocessing import Pool
from PIL import Image

poolLimite = 10
key = "svdepkLmYsIQLWilVdiKRLEfK7ee6JTw"
opts, args = getopt.getopt(sys.argv[1:], "hi:o:r:")
input_doc_path=""
output_doc_path = ""
filePaths=[]

for op, value in opts:
    if op == "-i":
        input_doc_path = value
    elif op == "-o":
        output_doc_path = value
    elif op == "-r":
        input_doc_path = value
        output_doc_path = value
    elif op == "-h":
        print('''
        使用方法 python3 tinypng.py -i picDocPath -o outputDocPath
        -o 参数可以为空，默认存在picDocPath/tinypng 内
        去 https://tinypng.com/developers 申请自己的key 每key每月免费压缩500个图
        默认并发数为10 可以自己调整''')


# def absFilePath(fileName):
#     return os.path.join(input_doc_path,fileName)

def getTinyPng(filePath):
    print('开始'+filePath)
    if(os.path.splitext(filePath)[1]=='.png'):
        # api 方式压缩图片
        request = Request("https://api.tinify.com/shrink", open(filePath, "rb").read())
        cafile = None
        auth = b64encode(bytes("api:" + key, "ascii")).decode("ascii")
        request.add_header("Authorization", "Basic %s" % auth)

        response = urlopen(request, cafile = cafile)
        if response.status == 201:
          # Compression was successful, retrieve output from Location header.
          result = urlopen(response.getheader("Location"), cafile = cafile).read()
        # 压缩图片结束
          output = os.path.join(output_doc_path, os.path.relpath(filePath,input_doc_path))
          open(output, "wb").write(result)
          print('完成' + filePath)
        else:
            print('失败' + filePath)
            # Something went wrong! You can parse the JSON body for details.
            print("Compression failed")
    else:
        im = Image.open(filePath)
        im.save(filePath, quality=70, optimize=True, progressive=True)
        print('完成'+filePath)



def main():
    global output_doc_path
    if output_doc_path == '':
        output_doc_path = os.path.join(os.path.split(input_doc_path)[0], 'outputTinypng')
    if not os.path.exists(output_doc_path):
        os.mkdir(output_doc_path)

    for parent,dirnames,filenames in os.walk(input_doc_path):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
      for dirname in  dirnames:                       #输出文件夹信息
        outDir = os.path.join(output_doc_path,os.path.relpath(os.path.join(parent,dirname),input_doc_path))
        if not os.path.exists(outDir):
            os.mkdir(outDir)

      for filename in filenames:                        #输出文件信息
        filePaths.append(os.path.join(parent,filename))

    # filter 后缀名  os.path.splitext(x)[1]
    pngFilePaths = filter(lambda x:os.path.splitext(x)[1]=='.png' or os.path.splitext(x)[1]=='.jpg',filePaths)

    print('Parent process %s.' % os.getpid())
    p = Pool(poolLimite)
    for fileName in pngFilePaths:
        p.apply_async(getTinyPng, args=(fileName,)) # 异步的
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')

if __name__=='__main__':
    if os.path.isdir(input_doc_path):
        main()
