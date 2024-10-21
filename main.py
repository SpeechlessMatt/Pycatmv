import os
from time import sleep
import sys
import aiohttp
import requests
import re
import aiofiles
import asyncio
import time
import shutil
from updating import detect_update

# version: 0.1.1
VERSION = "0.1.2"
"""
初级阶段的任务（已完成）
1. 从主页面拿到不同播放源 目前只抓暴风云
2. 从不同播放源中提取数据
3. 在指定播放源中通过re寻找不同集数的url
4. 进入url通过re寻找video标签，然后下载m3u8，保留主要url
5. 将m3u8的主要url通过协程下载完整视频"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "Cookies": "_pk_id.12.a3ce=f80a29df0e33ec7e.1729091921.; recente=%5B%7B%22vod_name%22%3A%22%E"
               "4%BC%8D%E5%85%AD%E4%B8%83%E4%B9%8B%E8%AE%B0%E5%BF%86%E7%A2%8E%E7%89%87%22%2C%22vod"
               "_url%22%3A%22https%3A%2F%2Fwww.xc8j.com%2Fxcplay%2F105580-3-3.html%22%2C%22vod_part"
               "%22%3A%22%E7%AC%AC04%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%22%E9%94%A6%E7%BB%A3%E5%"
               "AE%89%E5%AE%81%22%2C%22vod_url%22%3A%22https%3A%2F%2Fwww.xc8j.com%2Fxcplay%2F105889-"
               "2-0.html%22%2C%22vod_part%22%3A%22%E7%AC%AC01%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%"
               "22%E6%BC%A0%E9%A3%8E%E5%90%9F%22%2C%22vod_url%22%3A%22https%3A%2F%2Fwww.xc8j.com%2Fxc"
               "play%2F105473-2-0.html%22%2C%22vod_part%22%3A%22%E7%AC%AC01%E9%9B%86%22%7D%5D; _pk_ref"
               ".12.a3ce=%5B%22%22%2C%22%22%2C1729211555%2C%22https%3A%2F%2Fcn.bing.com%2F%22%5D; _pk"
               "_ses.12.a3ce=1; 9330_3587_36.112.29.98=1; 9330_3912_36.112.29.98=1; PHPSESSID=jm1n866"
               "qecm2p6fbefk2ios54p; 9330_3918_36.112.29.98=1; 9330_3900_36.112.29.98=1; 9330_3910_36"
               ".112.29.98=1; richviews_9330=EdhNMqij4B488L5sq77ahWkCNUwvQpGFe%252Fih187knJ0e1XhUC94F"
               "gGw4O8MiweikKVra2M084%252BGFQEe1%252B2VMu654EgTqsOVjba0yaY%252BeFHcCYHdk%252BuG1CKcBe"
               "TzchffiNSbIaRMeZbslWblmaYfeGL1hkymIp%252B28CSY9Jnme8G1r55v4ygRaIPUL%252BSMO5X%252BOcn"
               "BRPQzOlaWJh1qgpD%252Bzw9oV4TwEFE%252BZzICG5zGWIxnYOzo3m5FrVGGxUAp%252BWd2zTvsY%252FX4"
               "AMa5C%252BFgxx0qw5E1RnuquwMwa9YP5rgNCOPsYdoZTdVkvsO%252BKEjp8FLVmcRoTG1KBb5VOK3XG1wxx"
               "PgopLHUF%252BvoSkpINcQF%252F7r0VWDxU7EUqZTffQ9DRNM2jRorPDPuNJ3dQByDD90E1SS0ZZV8NryFCWp"
               "%252FrrKry34IcD712M8bl6R9iV6r3WiJWc1tqxZfXGQpBOVZQ8lPDeQWBEbq%252BbCt71GQMT1KSsJMbt21D"
               "5X5AUq36hgi0ouR5IasTrg3tOEAkux7oEdKSuTgP%252FSI%252FANhEchgLhJm5ABHgFcxIHEwem7oxY4QiKYR"
               "WXQOryQXI9eGKkWDTRDhTyj0PCY42zUD4u7KwP2w0s9jj0a%252FAtfV6ZYCmxkNl3NxjxeaAnWz1fO0xqHSqM"
               "fjXDpk8GLjMgLsmVVZjp1DFNPM%253D; 9330_3862_106.39.130.62=1"
}


def init_all(dir_='ts'):
    try:
        os.mkdir(dir_)
    except FileExistsError:
        print(f"文件夹已经存在，请重命名或删除：{dir_}")


# 搜索片名，但是这个是禁止高速爬虫的，我们应该严格遵守robots.txt的协议，因此需要保护该接口
def search_mv():
    while True:
        search = input("搜索片名：")
        header_0 = {
            "Referer": "https://www.xc8j.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Appl"
                          "eWebKit/537.36 (KHTML, like Gecko) Chrome/12"
                          "9.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Cookies": ("_pk_id.12.a3ce=f80a29df0e33ec7e.1729091921.; 93"
                        "30_3918_36.112.29.34=1; 9330_3862_36.112.29.34=1; "
                        "9330_3900_106.39.130.62=1; 9330_3587_36.112.29.98=1;"
                        " 9330_3916_106.39.130.62=1; 9330_3910_106.39.130.62=1"
                        "; 9330_3912_106.39.130.62=1; 9330_3916_36.112.29.34=1; 9"
                        "330_3918_36.112.29.98=1; 9330_3587_36.112.29.34=1; 9330_39"
                        "10_36.112.29.34=1; 9330_3587_106.39.130.62=1; 9330_386"
                        "2_106.39.130.62=1; 9330_3900_36.112.29.34=1; 9330_3918_1"
                        "06.39.130.62=1; _pk_ref.12.a3ce=%5B%22%22%2C%22%22%2C172"
                        "9167795%2C%22https%3A%2F%2Fcn.bing.com%2F%22%5D; _pk_ses."
                        "12.a3ce=1; 9330_3912_36.112.29.98=1; 9330_3900_36.112.29."
                        "98=1; recente=%5B%7B%22vod_name%22%3A%22%E4%BC%8D%E5%85%A"
                        "D%E4%B8%83%E4%B9%8B%E8%AE%B0%E5%BF%86%E7%A2%8E%E7%89%87%2"
                        "2%2C%22vod_url%22%3A%22https%3A%2F%2Fwww.xc8j.com%2Fxcpla"
                        "y%2F105580-3-3.html%22%2C%22vod_part%22%3A%22%22%7D%2C%7B"
                        "%22vod_name%22%3A%22%E9%94%A6%E7%BB%A3%E5%AE%89%E5%AE%81%"
                        "22%2C%22vod_url%22%3A%22https%3A%2F%2Fwww.xc8j.com%2Fxcpl"
                        "ay%2F105889-2-0.html%22%2C%22vod_part%22%3A%22%E7%AC%AC01"
                        "%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%22%E6%BC%A0%E9%A3%"
                        "%E5%90%9F%22%2C%22vod_url%22%3A%22https%3A%2F%2Fwww.xc8j"
                        ".com%2Fxcplay%2F105473-2-0.html%22%2C%22vod_part%22%3A%22%"
                        "E7%AC%AC01%E9%9B%86%22%7D%5D; 9330_3910_36.112.29.98=1; 933"
                        "0_3912_36.112.29.34=1; PHPSESSID=tn4tkdsemoifjij5m8a4nao5f4"
                        "; richviews_9330=LYwWgZEUtB9Oau%252F0VMpIO9e9Ky5RYjJUPaPCUs"
                        "b3wja5CGWRDHABfTTZSNb8fkq5BnFcUPuisIOW%252F%252FsqbYA5Dn4EA"
                        "RQhGCjFSP99NAiFfBoe2ml4Im12NdRoHbVkmmJQdOh98CrNUKulI1kOcRjX"
                        "GHFEjOeNJWvaEWz6QrMx4abgsLbUDxjAhaT2Ke%252FE3vhDYwgwNg1blE%"
                        "252F2Kp1LuzxVxich1JujDG2H2vz1YxsrmoW22tQo8ckhzBKpKHHjFNPRNK"
                        "XL%252B6GgW%252BIwHikhxHzUpLuRQPfzHa0uxvRaPs72xNAi%252B81s%"
                        "252FVeFvd8QW6XS%252FS2awHlbXq4ehDjHnY3v%252FNErKonK99YgcThC"
                        "SOCGZxFTzkzyWQiItvPgwmGjrUqsAzFSt8NotG4bqetUQ60aVTmQAiLpB%2"
                        "52B8jWqYw6zSWHXcCGbNCOpfFuvGVrixopMJMomZ3HIlQjmcivx7j0s2ep%"
                        "252FejTmRJ7KBeeJJl9jIyQup%252BtBShzBe3ytF2%252BH8qR1EsWC6ln"
                        "7jldV5DPa7Qs1AGES5mTU3Ks16TP%252FrsxEWvimoTfoSzMr01Y98iRw7j"
                        "YBQ8uQwOKkZy%252BwvMsIli1%252BVukCClFlFx0Z0fd1Al%252BXjRJQ%"
                        "252FvXJPIgvyWIfOPzc8zmCmOZfA7fawWQqPqLQVFoIMmxIQFJbrs3xdcmO"
                        "zdtjaJgWkCk8M%253D")
        }
        search_url = f"https://www.xc8j.com/search.php?searchword={search}"
        search_resp = requests.get(search_url, headers=header_0)
        # print(search_resp.text)
        objn = re.compile("没有找到任何记录")
        obj = re.compile(
            r'<a class="fed-list-title fed-font-xiv fed-text-center fed-text-sm-left fed-visible fed-part-eone" href="(?P<href>.*?)">(?P<title>.*?)</a>',
            re.S)
        result = search_resp.text
        if objn.search(result) == "none":
            print("没有找到任何记录,请与15s后重试...")
            # 保护接口
            protect_api()
            time.sleep(15)
            exit_protect()
            continue
        number = 0
        temp = obj.findall(result)
        if not temp:
            sys.exit()
        for it in temp:
            number += 1
            print(number, it[1])
        ret = "null"
        while True:
            try:
                inp = int(input("选哪个？"))
                inp = inp - 1
                ret = temp[inp][0]
                break
            except TypeError:
                print("输入错误")
                continue
            except IndexError:
                print("输入错误")
                continue
        search_resp.close()
        protect_api()
        return ret


def api_effective(api_list: list):
    effective_api = []
    if "暴风云" in api_list:
        effective_api.append("暴风云")
    if "非凡云" in api_list:
        effective_api.append("非凡云")
    # if "量子云" in list:
    #     effective_api.append("量子云")
    # if "无尽云" in list:
    #     effective_api.append("无尽云")
    if not effective_api:
        print("无可用源：暂未适配可用源，请联系作者更新", api_list)
        sys.exit(0)
    a = 1
    for api_name in effective_api:
        print(f"{a}. {api_name}")
        a += 1
    while True:
        try:
            inp = int(input("选哪个源好呢？"))
            api = effective_api[inp-1]
            return api
        except TypeError:
            print("输入错误!")
            continue
        except IndexError:
            print("输入错误！")
            continue

# 获取子页面地址，进入选集选播放源
def from_api_to_url(url):
    resp = requests.get(url, headers=HEADERS)
    # print(resp.text)
    # 这个可以获取一个可用播放源列表
    obj_api = re.compile(r'<li class="fed-tabs-btns fed-part-curs fed-font-xvi fed-mart-v fed-text-green">(.*?)</li>',
                         re.S)
    api_list = obj_api.findall(resp.text)
    if not api_list:
        print("获取源数据失败")
        protect_api()
        sys.exit(0)
    api_name = api_effective(api_list)

    # 从指定源中获取可用集数
    obj = re.compile(
        r'<li class="fed-tabs-btns fed-part-curs fed-font-xvi fed-mart-v fed-text-green">' + api_name + '</li>.*?</div>',
        re.S)
    obj2 = re.compile(r'<a title=".*?" href="(?P<href>.*?)" target=".*?">.*?</a>', re.S)
    mod = obj.findall(resp.text)
    href_list = obj2.findall(mod[0])
    # print(title_list)
    print(f"一共有{len(href_list)}集，你下载第几集啊？")
    href = "null"
    while True:
        try:
            # 用户选择下载第几集 以后可以在这里加上多线程下载多集 把href改成列表就行
            episode_num = int(input()) - 1
            host = "https://www.xc8j.com"
            href = host + href_list[episode_num]
            break
        except IndexError:
            print("输入错误！")
            continue
        except TypeError:
            print("输入错误！")
            continue
        except ValueError:
            print("输入错误！")
            continue
    resp.close()
    # 返回集数的href
    return api_name, href

def ff_method(url: str, name, download_dir):
    headers_ = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Referer": "https://svip.ffzyplay.com/",
        "Origin": "https://svip.ffzyplay.com/"
    }
    with open(f"{download_dir}/w1.m3u8", mode="wb") as f1:
        resp1 = requests.get(url, headers=headers_, timeout=20)
        f1.write(resp1.content)
        print("[*]第一层解析完成")
        resp1.close()
    with open(f"{download_dir}/w1.m3u8", mode="r") as f1:
        for it in f1:
            if str(it).startswith("#"):
                continue
            url2 = url.rsplit("/",1)[0] + "/" + str(it).strip()
            # print(url2)
    with open(download_dir + '/' + name, mode="wb") as f2:
        resp2 = requests.get(url2, headers=headers_, timeout=20)
        # print(resp2.text)
        f2.write(resp2.content)
        print("[*]第二层解析完成")
        resp2.close()
    os.remove(f"{download_dir}/w1.m3u8")
    # print("ok")
    # get Authority
    headers_authority = {
        ":authority": "svipsvip.ffzy-online5.com",
        "Referer": "https://svip.ffzyplay.com/",
        "Origin": "https://svip.ffzyplay.com"
    }
    return 1, headers_authority

def match_api_method(api_name, m3u8_href, name, download_dir):
    try:
        if api_name == "暴风云":
            # headers 是常量
            download_file(m3u8_href, name, HEADERS, download_dir)
            return 0, None
        if api_name == "非凡云":
            headers_ = ff_method(m3u8_href, name, download_dir)
            return 1, headers_
        # if api_name == "量子云":
        #     print("还未适配")
        #     print("5s后自动退出...")
        # if api_name == "无尽云":
        #     print("还未适配")
        #     print("5s后自动退出...")
    except requests.exceptions.ConnectTimeout:
        print("该源不可用！请尝试别的源")
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
        return -1, "error"

# 获取m3u8的url
def get_m3u8_url(url):
    obj = re.compile(r'<script>.*?var now="(?P<href>.*?)"')
    resp = requests.get(url, headers=HEADERS)
    # 拿到m3u8的url
    for it in obj.finditer(resp.text):
        href = it.group("href")
        resp.close()
        return href


# 下载文件 指定好下载地址，文件名字，下载路径
def download_file(url, name, headers_, download_dir="ts"):
    with requests.get(url, headers=headers_) as r:
        with open(f"{download_dir}/{name}", mode="wb") as f:
            f.write(r.content)


# 下载ts文件：协程
async def download_ts(session, host, ts_name, download_dir="ts"):
    url = host + ts_name
    async with session.get(url) as r:
        async with aiofiles.open(f"{download_dir}/{ts_name}", mode="wb") as f:
            await f.write(await r.content.read())
            print("下载成功", ts_name)


# 创建异步协程：为ts下载做准备
async def get_ts(host, file, download_dir="ts", headers=None):
    tasks = []
    async with aiohttp.ClientSession(headers=headers) as session:
        async with aiofiles.open(f"{download_dir}/" + file, mode="r", encoding="utf-8") as f:
            async for wrapper in f:
                line = str(wrapper).strip()
                if line.startswith("#") or line.startswith('/'):  # 经调查，/是广告源头，这样可以去除广告
                    continue
                if not line:# 防止空的报错
                    continue
                task = asyncio.create_task(download_ts(session, host, line, download_dir=download_dir))
                tasks.append(task)
            await asyncio.wait(tasks)


# ffmpeg拼接，保证视频质量
def cat_ffmpeg(m3u8_file, download_dir="ts"):
    with open(f"{download_dir}/files.txt", mode="w") as ffmpeg_file:
        with open(f"{download_dir}/{m3u8_file}", mode="r") as m3u8:
            for it in m3u8:
                line = str(it).strip()
                if line.startswith("#") or line.startswith("/"):
                    continue
                if not line:
                    continue
                ffmpeg_file.write(f"file '{line}'\n")
    with os.popen(
            f"ffmpeg -loglevel quiet -f concat  -safe 0  -i {download_dir}/files.txt -vcodec copy -acodec copy Downloads/{m3u8_file.rstrip('.m3u8')}.mp4") as ret:
        print(ret.read())
        return 0


# 删除缓存文件，一切准备就绪
def rm_all_temp(download_dir):
    if os.path.exists("temp"):
        os.remove("temp")
    shutil.rmtree(download_dir)


# 生成api保护文件
def protect_api():
    with open("sleep", mode="w") as f:
        f.write('8')


# 删除api保护文件
def exit_protect():
    os.remove('sleep')


# 检测api保护文件
def detect_api_protection():
    if os.path.exists('sleep'):
        print(f'为了保护接口，请等待15s...')
        sleep(15)
        exit_protect()
        return 0
    else:
        return 0


def main(setUrl="null"):
    # print(setUrl)
    host = "https://www.xc8j.com"
    detect_api_protection()
    print("* 免责声明：程序仅供学习，侵权删资源...")
    print("* 作者:@czy_4201b")
    print(f"* 当前版本：{VERSION}")
    print("* 本软件的接口来源于星辰影院，一个小服务器，不要过度折腾他\n毕竟运营服务器要钱的...")
    print("* 下载后的文件在本目录Documents文件夹里面")
    try:
        if setUrl == "null":
            # 调用网站search.php接口，需要保护接口
            # 拿到电视剧栏目页面url
            set_url = host + search_mv()
            # 从源中拿到指定集的播放页url
            child_page = from_api_to_url(set_url)
            # 请求播放子页拿到m3u8地址
            m3u8_href = get_m3u8_url(child_page[1])
        else:
            set_url = setUrl
            # 从源中拿到指定集的播放页url
            child_page = from_api_to_url(set_url)
            # 请求播放子页拿到m3u8地址
            m3u8_href = get_m3u8_url(child_page[1])
            os.remove("temp")

    except requests.exceptions.ConnectTimeout:
        print("---连接超时，请求重试（8s后退出）---")
        protect_api()
        time.sleep(8)
        exit_protect()
        sys.exit(1)
    except requests.exceptions.MissingSchema:
        print("接口问题，请联系作者，如果你不知道作者是谁，那就没办法了")
        protect_api()
        sys.exit(1)
    except IndexError:
        print("额，这些源好像有问题，或者我还没适配，等我更新哥们")
        protect_api()
        sys.exit(1)
    # print(m3u8_href, child_page)
    # 用于命名
    dir_name = child_page[1].split("/")[-1].rstrip(".html")
    # 用于指定特定源获取m3u8的方式
    api_name = child_page[0]
    # 创建临时文件夹
    # 名字继承子页面html名字
    init_all(dir_name)
    # m3u8名字继承子页面html的名字
    m3u8_file_name = dir_name + ".m3u8"
    # 特殊
    print("[*]>>>开始解析...")
    api_ret = match_api_method(api_name, m3u8_href, name=m3u8_file_name, download_dir=dir_name)
    headers = None
    # 源加载错误
    if api_ret[0] == 1:
        with open("temp", mode="w") as temp:
            temp.write("[setUrl]" + set_url)
            print("源加载错误，请选择别的源重试")
            sys.exit(0)
    # 返回值搭载请求头
    if api_ret[0] == 1:
        headers = api_ret[1]

    # download_m3u8(m3u8_href, name=m3u8_file_name, download_dir=dir_name)

    # 协程下载:单线程
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_ts(m3u8_href.rsplit('/', 1)[0] + "/", m3u8_file_name, download_dir=dir_name, headers=headers))
    print("下载完毕, 开始合并...")
    cat_ffmpeg(m3u8_file_name, download_dir=dir_name)
    # rm_all_temp(dir_name)
    print("ok")


if __name__ == '__main__':
    print("* 正在检查更新...")
    update_status = detect_update("https://raw.githubusercontent.com/SpeechlessMatt/Pycatmv/refs/heads/main/version.json")
    if update_status == 1:
        print("有可用更新，是否更新？[y/n]")
        up_choice = input()
        if up_choice == "y" or up_choice == "Y":
            os.system("update.bat")
            sys.exit(0)
        else:
            print("---用户：拒绝更新")
    try:
        temp_file = open("temp", mode="r")
    except FileNotFoundError:
        main()
    else:
        for temp_line in temp_file:
            if not temp_line:
                continue
            if str(temp_line).startswith("[setUrl]"):
                if_temp = input("上次因为播放源出错退出，是否更换播放源？[y/n]")
                if if_temp in ["y", "Y"]:
                    main(temp_line.lstrip("[setUrl]"))
                else:
                    main()
        temp_file.close()

