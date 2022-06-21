#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 10:38:00 2022

@author: tup0lev
"""

from __future__ import unicode_literals
from googletrans import Translator, constants
from pprint import pprint
import random
from biliup.plugins.bili_webup import BiliBili, Data
from bs4 import BeautifulSoup
import urllib.request
import re
from google.cloud import translate_v2
import youtube_dl
import os
#from .uploader import upload
import ffmpeg

def getVid(): # get random youtube video
    print("获取一个0播放的youtube视频")
    
    fp = urllib.request.urlopen("https://petittube.com/") #get random unwatched utb vid
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()
    vidID = mystr.partition("embed/")[2].rpartition("?version")[0] 
    youtubeurl= "https://www.youtube.com/watch?v=" + vidID
    print(   "youtube视频地址是"   +  youtubeurl     )
    soup = BeautifulSoup(urllib.request.urlopen(youtubeurl))
    title = soup.title.string.replace("- YouTube", "").replace("#", "")
    return   youtubeurl, title

def validateVid(vidurl, title):
    print("检查重复获取")
    
    with open('cked.txt', 'w+') as f:
        lines = f.readlines()
        print(lines)
    for line in lines:
        if vidurl + "\n"  == line:
            print("已经获取过")
            return False
    vidfile = open('cked.txt', 'a')
    vidfile.write("\n")
    vidfile.write(vidurl)
    vidfile.close()
    print("检查视频成分")
    print ("视频标题为" + title)
    print("检查视频标题是否有汉字")
    for _char in title:
        if '\u4e00' <= _char <= '\u9fa5':
            print("视频标题有汉字，8行")
            #utb上中文视频大都是台巴子发的，太容易政治不正确
            #因此只要有汉字就一棒子打死
            return False
    print("视频标题没有汉字, 好耶！")
    print("ENG?")
    translator = Translator()
    print(translator.detect(title))
    if (translator.detect(title).lang) != "en" :
        print("Not ENG")
        return False
    
    print("机翻完了的超尬标题是: " + translateTitle(title))
    print("开始简单审查视频-关键词匹配")
    #TODO 
    #暂时先8做这个了
    print("顺利通过成分检查")
    return True 

def translateTitle(title):
    translator = Translator()
    translation = translator.translate(title, dest='zh-CN')    
    return translation.text

def downloadVid(vidurl):
    print("下载视频")
    
    ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]',       
    'outtmpl': 'Download',        
    'noplaylist' : True,        
    'postprocessors': [{
    'key': 'FFmpegVideoConvertor',
    'preferedformat': 'mp4'
    }]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([vidurl])
    #TODO
    pass




def fuckupvid():
    stream = ffmpeg.input('Download.mp4')
    bgm = ffmpeg.input('bgm.aac')
    
 #   print("掐头去尾")
    
    probe = ffmpeg.probe('Download.mp4')
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    print(video_info)
    num_frames= int(video_info['nb_frames'])
    
    
    stream = stream.trim(start_frame=round(num_frames*0.1), end_frame=round(num_frames*0.9))
        
    print("镜像")
    stream = ffmpeg.hflip(stream)
    
    print("随机添加弱智bgm")
        
    duration = (video_info['duration'])
    bgmprobe = ffmpeg.probe('bgm.aac')
    bgm_info = next(s for s in bgmprobe['streams'] if s['codec_type'] == 'audio')
    bgmduration =(bgm_info['duration'])
    print(bgm_info)
   # bgmframes = int(bgm_info['nb_frames'])
   
    bgmduration = round(float(bgmduration))
    
    print("bgmduration" ,bgmduration)
    duration = round(float(duration))
    bgmtrimstart = random.randint(0, bgmduration - duration)
    bgm = bgm.audio.filter('atrim', start = bgmtrimstart,
                           end = bgmtrimstart + duration)
    bgm = ffmpeg.output(bgm, 'tmp.aac')
    ffmpeg.run(bgm)
    newbgm = ffmpeg.input('tmp.aac')
    stream = ffmpeg.concat(stream, newbgm, v=1, a=1)
    stream = ffmpeg.output(stream, 'output.mp4')
    ffmpeg.run(stream)
    
    

def uploadvid(vidurl, title):
    print("上传视频到霹雳霹雳")
    
    video = Data()
    video.title = title
    video.desc = title
    video.source = vidurl
    # 设置视频分区,默认为122 野生技能协会
    video.tid = 171
  ##  video.set_tag(['星际争霸2', '电子竞技'])
    with BiliBili(video) as bili:
        bili.login("bili.cookie", {
            'cookies':{
                'SESSDATA': '606a5ef8%2C1666695853%2Cc0f57%2A41',
                'bili_jct': '367ae89cd01af60eaf4e7fcbaec73d71',
                'DedeUserID__ckMd5': '6bf640251dfdfc52',
                'DedeUserID': '2087764486'
            },'access_token': '3c4e87783c11c12b9dd3d1e26db20841'})
     #   bili.login_by_password("173486909666", "Pilipili")
      #  for file in file_list:
        video_part = bili.upload_file("Download.mp4")  # 上传视频
         #   video.append(video_part)  # 添加已经上传的视频
       # video.cover = bili.cover_up('/cover_path').replace('http:', '')
        ret = bili.submit()  # 提交视频
    pass


while (True):
    try:
        os.remove("Download.mp4")
        os.remove("tmp.aac")
        os.remove('output.mp4')
    except Exception:
        pass

    vidurl, vidtitle = getVid() #获取视频以及标题
    
    if ( validateVid(vidurl, vidtitle) ): #审查视频
        downloadVid(vidurl)
        fuckupvid()
        
        
        os.rename('output.mp4', translateTitle(vidtitle) + ".mp4")
        
    #    os.rename('Download.mp4',  vidtitle + ".mp4"  )
    
    try:
        os.remove("Download.mp4")
        os.remove("tmp.aac")
        os.remove('output.mp4')
    except Exception:
        pass
  
    
def transcoding(data):
    pass