# from rich.progress import track, Progress
# import time
#
# for i in track(range(20), description="[red]Process.."):
#     time.sleep(0.1)
#
# with Progress() as progress:
#     task1 = progress.add_task("[red]Downloading...", total=100)
#     while not progress.finished:
#         progress.update(task1, advance=0.5)
#         time.sleep(0.1)
"""
1. request
"""
import json
import os
# import shutil
import sys

# from operator import index
import requests

def write_d(new_version):
    dic = {"version": new_version, "project": "Pycatmv", "beta_build": "main"}
    with open("version.json", mode="w") as f:
        f.write(json.dumps(dic, indent=4, sort_keys=True, ensure_ascii=False))

def read_d():
    with open("version.json", mode="r") as f:
        dic = json.loads(f.read())
        print(list(dic.keys()))

def detect_update(version_file_url):
    try:
        v = open("version.json", mode="r")
        resp = requests.get(version_file_url, timeout=10)
        net_info = json.loads(resp.text)
        resp.close()
    except FileNotFoundError:
        print("*******警告：当前版本信息丢失，本项目文件不完整...无法获取更新!*******")
        return 0
    except requests.exceptions.ConnectTimeout:
        print("暂无可用更新：连接超时")
        return 0
    except requests.exceptions.ReadTimeout:
        print("暂无可用更新：连接超时")
        return 0
    except requests.exceptions.ConnectionError:
        print("网络连接错误，暂无可用更新")
        return 0
    else:
        exist_info = json.loads(v.read())
        v.close()
    exist_list = exist_info["version"].split(".")
    net_list = net_info["version"].split(".")
    if len(net_list) > len(exist_list):
        with open("update", mode="w") as u:
            u.write(net_info["version"])
        return 1
    # print(net_list, exist_list)
    for i in range(len(net_list)):
        if exist_list[i] < net_list[i]:
            with open("update", mode="w") as u:
                u.write(net_info["version"])
            return 1
    print("--无可用更新，当前版本是最新版本--")
    return 0

def update_all():
    print("全量更新暂时不支持，请联系作者")
    pass

def main(url):
    # add_files = []
    # rm_files = []
    print("正在获取更新...")
    try:
        resp = requests.get(url)
    except requests.exceptions.ConnectionError:
        print("连接失败")
        sys.exit(0)
    except requests.exceptions.ConnectTimeout:
        print("连接超时")
        sys.exit(0)
    dic = json.loads(resp.text)
    version_list = list(dic.keys())
    with open("update", mode="r") as v:
        exist_version = v.read()
    if exist_version in version_list:
        exist_version_index = version_list.index(exist_version)
        updating_url = None
        for it in range(exist_version_index + 1, len(version_list)):
            update_version = version_list[it]
            if dic[update_version]['log'] == "all_update":
                print("接收到全量版本更新！")
                return 0
            if dic[update_version]['log'] == "updating_update":
                updating_url = dic[version_list[-1]]['updating_url']
        # 目前热更新仅支持main.py, updating.py更新
        if updating_url:
            try:
                with requests.get(updating_url) as u:
                    with open("updating_0.py", mode="wb") as m:
                        m.write(u.content)
            except requests.exceptions.ConnectTimeout:
                print("更新失败！原因：无法连接")
                sys.exit()
            else:
                # 删除main
                os.remove("updating_0.py")
                os.rename("updating_0.py", "update.py")
                print("更新成功！！！")
                resp.close()
        hot_update_url = dic[version_list[-1]]['direct_url']
        try:
            with requests.get(hot_update_url) as r:
                with open("main_0.py", mode="wb") as m:
                    m.write(r.content)
        except requests.exceptions.ConnectTimeout:
            print("更新失败！原因：无法连接")
            sys.exit()
        else:
            # 删除main
            os.remove("main.py")
            os.rename("main_0.py", "main.py")
            write_d(version_list[-1])
            resp.close()

    else:
        print("****您当前版本已经不在热更新范围内，需要全量更新****")
        print("请等待...")
        return 0

# os.mkdir("./ts/sb")
# shutil.rmtree("./ts/sb")
# write_d()
# read_d()
# detect_update("https://raw.githubusercontent.com/SpeechlessMatt/Pycatmv/refs/heads/main/version.json")
if __name__ == '__main__':
    if main("https://raw.githubusercontent.com/SpeechlessMatt/Pycatmv/refs/heads/main/effective_version.json") == 0:
        update_all()
        os.remove("update")
        sys.exit()
