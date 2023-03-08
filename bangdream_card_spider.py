import time
import traceback
import requests
from pathlib import Path
import sys

path = "bangdream_card"  # 设置图片的下载路径

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76'
}

proxy = {}
# 若不用代理，将链接清空即可。

url_1 = "https://bestdori.com/api/cards/all.5.json"
url_2 = "https://bestdori.com/api/characters/main.3.json"
url_3 = "https://bestdori.com/api/bands/main.1.json"
print('开始进行爬取，请稍后......')

time_start = time.time()
try:
    resp_all = requests.get(url_1, headers = headers, proxies = proxy, timeout=90)
    resp_name = requests.get(url_2, headers = headers, proxies = proxy, timeout=90)
    resp_band = requests.get(url_3, headers = headers, proxies = proxy, timeout=90)
    resp_all.encoding = 'utf-8'
    resp_name.encoding = 'utf-8'
    resp_band.encoding = 'utf-8'
    all_data = resp_all.json()
    name_data = resp_name.json()
    band_data = resp_band.json()
except:
    print(f'{sys.exc_info()[0]} 网页请求超时，请检查网络连接')
    sys.exit() # 结束程序

def name(data):
    '''
    获取角色名称+乐队名称
    '''
    for k, v in name_data.items():
        if k == str(data):
            characterName = v["characterName"][0]
            bandName = band_data[str(v["bandId"])]["bandName"][0]

    return characterName, bandName

img_num = 0
error_num = 0
success_num = 0
def download(img_url, bandName, img_name):
    '''
    下载模块

    img_url: 图片下载链接
    bandName: 乐队名
    img_name: 图片名
    '''
    global img_num, error_num, success_num

    img_num += 1
    if not Path(path, bandName, img_name).exists():
        try:
            img_data = requests.get(img_url, headers = headers, proxies = proxy, timeout = 180).content
            # .content 拿到字节(二进制对象)
            Path(path, bandName, img_name).write_bytes(img_data) # 以二进制方式写入文件
            success_num += 1
            print(f'第 {img_num} 个图片下载成功：{img_name}')
        except:
            error_num += 1
            print(f'{sys.exc_info()[0]} 第 {img_num} 个图片下载失败：{img_name}')
            return
    else:
        print(f'文件 {img_name} 已存在，不再进行下载')

def server_switch(server, key, value):
    '''
    服务器切换

    server: 服务器
    key: 键
    value: 值
    '''
    # 优先使用日语卡面名称，为空则使用简体中文，再为空则使用繁体中文
    prefix = value["prefix"][0]
    if prefix == None:
        prefix = value["prefix"][3]
        if prefix == None:
            prefix = value["prefix"][2]

    res = value["resourceSetName"]
    characterName = name(value["characterId"])[0]
    bandName = name(value["characterId"])[1]
    Path(path, bandName).mkdir(parents = True, exist_ok = True)
    if value["rarity"] in [1, 2]:
        stars = f"★{value['rarity']}"
        img_url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res}_rip/card_normal.png"
        img_url_trim = f"https://bestdori.com/assets/{server}/characters/resourceset/{res}_rip/trim_normal.png"
        img_name = f"{key}【{stars}】【{characterName}】【{prefix}】card_normal.png"
        img_name_trim = f"{key}【{stars}】【{characterName}】【{prefix}】trim_normal.png"

        # 图片下载
        download(img_url, bandName, img_name)
        download(img_url_trim, bandName, img_name_trim)

    if value["rarity"] in [3, 4]:
        stars = f"★{value['rarity']}"
        img1_url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res}_rip/card_normal.png"
        img1_url_trim = f"https://bestdori.com/assets/{server}/characters/resourceset/{res}_rip/trim_normal.png"
        img2_url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res}_rip/card_after_training.png"
        img2_url_trim = f"https://bestdori.com/assets/{server}/characters/resourceset/{res}_rip/trim_after_training.png"
        img1_name = f"{key}【{stars}】【{characterName}】【{prefix}】card_normal.png"
        img1_name_trim = f"{key}【{stars}】【{characterName}】【{prefix}】trim_normal.png"
        img2_name = f"{key}【{stars}】【{characterName}】【{prefix}】card_after_training.png"
        img2_name_trim = f"{key}【{stars}】【{characterName}】【{prefix}】trim_after_training.png"

        # 图片下载
        download(img1_url, bandName, img1_name)
        download(img1_url_trim, bandName, img1_name_trim)
        download(img2_url, bandName, img2_name)
        download(img2_url_trim, bandName, img2_name_trim)

def main():
    '''
    主执行函数
    '''
    for k, v in all_data.items():
        if int(k) < 5000:
            server = "jp"
            server_switch(server, k, v)
        if int(k) >= 5000 and int(k) <= 6000:
            server = "tw"
            server_switch(server, k, v)
        if int(k) >= 10000 and int(k) <= 11000:
            server = "cn"
            server_switch(server, k, v)

    time_end = time.time()
    use_time = int(time_end - time_start)
    print(f'全部下载完成！共下载成功{success_num}个文件，失败{error_num}个文件，用时{use_time}秒')
    print('程序将在10秒后结束...')
    time.sleep(10)

if __name__ == "__main__":
    main()