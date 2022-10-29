import bs4
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import requests

url_root = 'https://copymanga.site'
scroll_time = 300
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

def download_comic(comic_name, comic_path):
    chapter_list = get_comic_chapter(comic_name, comic_path)
    for chapter in chapter_list:
        chapter_name = chapter[0]
        chapter_url = chapter[1]
        pic_list = get_chapter_piclist(comic_name, chapter_name, chapter_url)
        download_piclist(comic_name, chapter_name, pic_list)


def get_comic_chapter(comic_name, comic_path):

    print("获取漫画{}章节".format(comic_name))
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path="chromedriver", options=options)
    driver.get(comic_path)
    time.sleep(2)
    for i in range(1, 3):
        driver.execute_script(
            'window.scrollTo(0,document.body.scrollHeight)')
        time.sleep(1)
    temp_folder = "temp/_{}".format(comic_name)
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    comic_html_url = "temp/_{}/_{}.html".format(comic_name, comic_name)
    with open(comic_html_url, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    soup = BeautifulSoup(
        open(comic_html_url, encoding='utf-8'), features='html.parser')
    ul = soup.find('ul', class_="nav nav-tabs")

    index = 0
    li_list = []
    for li in ul:
        index += 1
        print(str(index) + " " + li.string)
        li_list.append(li.string)
    choose = input("请选择要下载的内容序号")
    index = int(choose) - 1
    choose_id = "default{}".format(li_list[index].string)
    chapter_ul = soup.find(id=choose_id).find('ul')

    chapter_list = []

    for chapter in chapter_ul:
        chapter_list.append((chapter.string, url_root + chapter.attrs['href']))

    print("获取漫画{}章节成功！".format(comic_name))

    choose = input('是否下载所有章节？（y/n）')
    if choose == 'y':
        return chapter_list
    else:
        i = 0
        for chapter in chapter_list:
            i += 1
            print(str(i) + " " + chapter[0])
        choose = input('请输入你要下载章节的序号, 用空格隔开？（例如: 1-5 9-20 25 28）')
        choose_slice = choose.split(" ")
        choose_chapter_list = []
        for sli in choose_slice:
            if '-' in sli:
                a, b = sli.split('-')
                a = int(a) - 1
                b = int(b) - 1
                choose_chapter_list.extend(chapter_list[a:b])
            else:
                choose_chapter_list.append(chapter[int(sli)])
        return choose_chapter_list


def get_chapter_piclist(comic_name, chapter_name, chapter_url):
    print("获取漫画{} {}图片地址".format(comic_name, chapter_name))
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path="chromedriver", options=options)
    driver.get(chapter_url)
    time.sleep(3)
    scroll = 100
    for i in range(1, scroll_time):
        scroll += 250
        js = "var q=document.documentElement.scrollTop={}".format(scroll)
        driver.execute_script(js)
        time.sleep(0.15)
    time.sleep(3)
    chapter_html_url = "temp/_{}/_{}.html".format(
        comic_name, chapter_name)

    with open(chapter_html_url, "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    soup = BeautifulSoup(
        open(chapter_html_url, encoding='utf-8'), features='html.parser')
    pic_ul = soup.find('ul', class_="comicContent-list")

    pic_list = []
    for i in pic_ul:
        img = i.find('img')
        if type(img) == bs4.element.Tag:
            pic_list.append(img.attrs['src'])

    print("获取漫画{} {}图片地址成功！".format(comic_name, chapter_name))
    return pic_list


def download_piclist(comic_name, chapter_name, pic_list):
    download_folder = "{}/{}".format(comic_name, chapter_name)
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    print('下载{}，共{}张图片'.format(chapter_name, len(pic_list)))
    j = 0
    for i in pic_list:
        j += 1
        pic = requests.get(i, proxies=proxies).content

        pic_path = download_folder + '/' + os.path.split(i)[-1]

        if os.path.exists(pic_path):
            continue
        with open(pic_path, 'wb') as f:
            print('正在下载 ' + comic_name + " " +
                  chapter_name + " 第" + str(j) + "张图片")
            f.write(pic)


while(1):
    q = input("请输入搜索的内容：")

    params = {"offset": 0,
              "platform": 2,
              "limit": 12,
              "q": q
              }
    url = "https://copymanga.site/api/kb/web/searchs/comics"

    response = requests.request("GET", url, params=params, proxies=proxies)

    comic_list = response.json()['results']['list']

    index = 0
    for i in comic_list:
        index += 1
        print(str(index) + ' ' + i['name'] + ': ' + i['alias'])

    choose = input("下载哪个漫画？（请输入下载漫画的序号）")
    try:
        index = int(choose) - 1
    except:
        choose = input("是否要退出下载？（y/n）")
        if choose == 'y':
            print('再见')
            break
        else:
            continue
    comic_name = comic_list[index]['name']
    comic_path_word = comic_list[index]['path_word']
    comic_path = "https://copymanga.site/comic/{}".format(comic_path_word)
    print('开始下载')
    download_comic(comic_name, comic_path)
