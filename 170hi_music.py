# -*- coding: utf-8 -*-
import requests
import re
import os
from pypinyin import lazy_pinyin
import eyed3

'''
先从搜索链接获取歌曲信息(json)
abslist 返回的结果字段,先判断这key是否有值
MUSICRID 曲ID  MUSIC_157607;
SONGNAME 曲名 慢慢;
ARTIST 歌手 张学友;
FALBUM 专辑 Black&nbsp;&&nbsp;White;
WEBMP3Q0_PATH 歌曲的下载后缀 /n2/128/66/52/3763799718.mp3
http://other.web.ra01.sycdn.kuwo.cn/resource/n2/128/66/52/3763799718.mp3
酷我音乐api "http://www.kuwo.cn/webmusic/st/getMuiseByRid?rid=MUSIC_"
&nbsp; 空格标签
&amp; &标签
'''

music_dir="E:\\音乐\\"
search_url ="http://search.kuwo.cn/r.s"
referer_url = "http://www.170hi.com/so?q="
kuwo_api="http://www.kuwo.cn/webmusic/st/getMuiseByRid?rid="
download_url = "http://other.web.ra01.sycdn.kuwo.cn/resource/"
data = {
    "all": u"练习",
    "ft":"music",
    "client":"kt",
    "cluster":"0",
    "rn":"1",
    "rformat":"json",
    "callback":"searchMusicResult",
    "encoding":"utf8",
    "vipver":"MUSIC_8.0.3.1"
}
headers={
    "Content-Type":"application/json",
    "Cache-Control":"max-age=0",
    "Host":"search.kuwo.cn",
    "Referer":"http://www.170hi.com/so",
    "Proxy-Connection":"keep-alive",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
}

download_header={
    "Host":"dl.stream.qqmusic.qq.com",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
}

def get_music_download_url(name,artist=None,rn='5'):
    china_name = name
    pinyin_name = "".join(lazy_pinyin(name))
    name = name.encode('utf-8')
    headers["Referer"] = referer_url+str(name)+"&nsid=4"
    data["all"] = name
    data["rn"] = rn
    respones = requests.get(search_url,headers=headers,params=data)
    text_result = respones.text

    re_result = re.search(r'=(.*)]}',text_result)
    str_result= re_result.group().strip("=")
    json_result = eval(str_result)
    # print(json_result["abslist"][0])
    music_model = {"ARTIST":artist,"NAME":china_name,"FALBUM":"","ID":"","URL":"","TITLE":"","PNAME":pinyin_name,"MPATH":music_dir}
    if json_result["abslist"]:
        music_model["ARTIST"] = json_result["abslist"][0]["ARTIST"]
        music_model["FALBUM"] = json_result["abslist"][0]["ALBUM"]
        music_model["GENRE"] = json_result["abslist"][0]["GENRE"]
        music_model["URL"] = json_result["abslist"][0]["MP3PATH"]
        music_model["URL2"] = json_result["abslist"][0]["WEBMP3Q0_PATH"]
        music_model["ID"] = json_result["abslist"][0]["MUSICRID"]
        music_model["TITLE"] = str(china_name)
        music_model["SAVE_PATH"] = music_dir + json_result["abslist"][0]["ARTIST"]
        if artist:
            for i in json_result["abslist"]:
                if i["ARTIST"] == artist.replace(" ","&nbsp;"):
                    music_model["ARTIST"]= str(artist)
                    music_model["FALBUM"]=i["ALBUM"]
                    music_model["GENRE"]=i["GENRE"]
                    music_model["URL"]=i["MP3PATH"]
                    music_model["URL2"]=i["WEBMP3Q0_PATH"]
                    music_model["ID"]=i["MUSICRID"]
                    music_model["TITLE"]=str(china_name)+"-"+str(artist)
                    music_model["SAVE_PATH"]=music_dir+str(artist)
        print("酷我音乐 歌手：%s 歌曲：%s 专辑：%s 流派：%s"% (music_model["ARTIST"],music_model["NAME"],music_model["FALBUM"],music_model["GENRE"]))
        return music_model
    else:
        return None

def get_kuwo_api_callback(music_dict):
    music_id=music_dict["ID"]
    kuwo_url=kuwo_api+music_id
    res=requests.get(kuwo_url)
    name = re.search(r'mp3dl>(.*)</mp3dl',res.text)
    name = "http://"+name.group(1)+"/resource/"
    music_dict["URL"]=name+music_dict["URL"]
    music_dict["URL2"]=name+music_dict["URL2"]
    return music_dict


def mk_music_dir(path):
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)

def download_music(music_dict,dir=None):
    if not dir:
        dir = music_dict["SAVE_PATH"]
    mk_music_dir(dir)
    print("下载地址1: %s"% music_dict["URL"])
    print("下载地址2: %s"% music_dict["URL2"])
    try:
        wget = requests.get(music_dict["URL"])
        if wget.status_code == 404:
            print("地址1下载失败,开始地址2下载尝试")
            wget = requests.get(music_dict["URL2"])
    except:
        print("地址1下载失败,开始地址2下载尝试")
        wget = requests.get(music_dict["URL2"])

    file_name = '%s%s.mp3'% (music_dict["MPATH"],music_dict["PNAME"])
    with open(file_name,'wb') as f:
        f.write(wget.content)
        print("已下载 %s"% music_dict["NAME"])
    return file_name

def charactor_mp3(filename,music_dict):
    '''&nbsp; 空格标签 &amp; &标签'''
    f = eyed3.load(filename)
    f.initTag()
    artist=music_dict["ARTIST"].replace("&nbsp;"," ")
    album=music_dict["FALBUM"].replace("&nbsp;"," ")
    title=music_dict["NAME"]
    album=album.replace("&amp;","&")
    print(artist,album,title)
    f.tag.artist=artist
    f.tag.album_artist = artist
    f.tag.album=album
    f.tag.title =title
    f.tag.save()
    music_file_name=music_dict["SAVE_PATH"]+"\\"+'%s.mp3'% music_dict["NAME"]
    os.rename(filename,music_file_name)

def search_music_from_ifkdy(name,artist=None):
    """疯狂音乐搜索,基于咪咕音乐库"""
    kuwo_data = get_music_download_url(name,artist)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "music.ifkdy.com",
        "Origin": "http://music.ifkdy.com",
        "Referer": "http://music.ifkdy.com/?name=music&type=qq",
        "Proxy-Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }
    search_author = artist
    _url = "http://music.ifkdy.com/"
    if artist: input_name = "%s %s"% (name,artist)
    args = {"input":input_name,"type":'qq',"filter":'name',"page":1}
    data = requests.post(_url,data=args,headers=headers)
    res = data.json()

    if artist:
        download_url = None
        for i in res["data"]:
            if artist in i['author'] and name in i['title']:
                download_url = i['url']
                music_name = i['title']
                artist = i['author']
            elif name in i['title']:
                download_url = i['url']
                music_name = i['title']
                artist = i['author']
            if download_url: break
    else:
        download_url = res["data"][0]["url"]
        music_name = res["data"][0]["title"]
        artist = res["data"][0]['author']
    if not download_url:
        print("QQ音乐无此歌曲信息！")
    else:
        print("QQ音乐 歌手：%s 歌曲：%s "% (artist, music_name))
        file_name = 'E:\\tmp\\TmpMusicFile.mp3'
        wget = requests.get(download_url,headers=download_header)
        with open(file_name,'wb') as f:
            f.write(wget.content)
            print("已下载 %s"% music_name)

        eye = eyed3.load(file_name)
        eye.initTag()
        eye.tag.artist = artist
        eye.tag.album_artist = artist
        eye.tag.title = music_name
        if kuwo_data:
            album = kuwo_data["FALBUM"].replace("&nbsp;"," ")
            album = album.replace("&amp;", "&")
            eye.tag.album=album #专辑名
            if kuwo_data["GENRE"]:
                eye.tag.genre = kuwo_data["GENRE"]
            else:
                eye.tag.genre = 'Pop'
        eye.tag.save()
        new_file_dir=music_dir+search_author
        mk_music_dir(new_file_dir)
        new_file_name=new_file_dir+"\\"+'%s.mp3'% music_name
        print("已下载到目录：%s"% new_file_name)
        try:
            os.rename(file_name,new_file_name)
        except:
            print("此文件已存在")

if __name__ == "__main__":
    # get_value=get_music_download_url(u"走马",artist=u"陈粒",rn='20')
    # Dict=get_kuwo_api_callback(get_value)
    # filename=download_music(Dict)
    # charactor_mp3(filename,Dict)
    search_music_from_ifkdy(u"I'm Gonna Getcha Good",artist=u"Shania Twain")