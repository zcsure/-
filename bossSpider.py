# @ Author: zcsure
# @ Python: Python3.6.1
# @ Desc
# -*- coding: UTF-8 -*-
# 获取职位信息
import requests
import re
import csv
from multiprocessing import Pool
from functools import partial
import time

# 获取有哪些职位，需要使用headers和cookies来成功访问页面
def getPositions():
    firstUrl = "https://www.zhipin.com/?ka=header-home" # boss直聘首页
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
        "referer": "https://www.zhipin.com/c101010100-p100199/"
    }
    cookies = {
        " lastCity":"101010100",
        " __c":"1572003017",
        " __g":"-",
        " _uab_collina":"157200301768772886222979",
        " __l":"l=%2Fwww.zhipin.com%2F&r=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3Df3zkJ_UoXHrXhaTYLs45hEzvgUcaZhUrqSCQxJgwUrxdQ0zdvlx1efrtsQp98BCP%26ck%3D4542.1.8.211.177.217.173.314%26shh%3Dwww.baidu.com%26sht%3Dbaidu%26wd%3D%26eqid%3Dcf038b40002315b4000000035db2dcc4&friend_source=0&friend_source=0",
        " JSESSIONID":"",
        " Hm_lvt_194df3105ad7148dcf2b98a91b5e727a":"1572357395,1572491501,1572690920,1573202085",
        " __zp_stoken__":"12d8EiJMObXealRvu4vWDNxm%2F1ouAsEeVrsGYpKVfln4PhPm3r7l1KtkWbV%2FykYCG5q4x24zSuo1a2ou9q%2FXbJNG%2Bg%3D%3D",
        " __a":"77707143.1572003017..1572003017.130.1.130.130",
        " Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a":"1573470927"
    }
    first_html = requests.get(firstUrl,headers=headers,cookies=cookies).text
    matchObj = re.search(r'技术(.*?)<ul>(.*?)</ul>',first_html,re.M|re.S) #re.S表示忽略换行
    positions = re.findall(r'<a.*?>(.*?)</a>',matchObj.group(2),re.S)
    return positions

# 获取某一页面，这个页面带有职位的详细信息，最后返回这个页面的json数据
def parse_url(url):
    headers1 = {
        'Accept': 'application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'Referer': 'https://www.zhipin.com/',
        'X-Requested-With': "XMLHttpRequest",
        "cookie": "lastCity=101010100; __c=1572003017; __g=-; _uab_collina=157200301768772886222979; __l=l=%2Fwww.zhipin.com%2F&r=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3Df3zkJ_UoXHrXhaTYLs45hEzvgUcaZhUrqSCQxJgwUrxdQ0zdvlx1efrtsQp98BCP%26ck%3D4542.1.8.211.177.217.173.314%26shh%3Dwww.baidu.com%26sht%3Dbaidu%26wd%3D%26eqid%3Dcf038b40002315b4000000035db2dcc4&friend_source=0&friend_source=0; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1572003018,1572357395; __zp_stoken__=9405XzQBYvJvrChGP156lFmiCBv%2FNyV5kxNWxKwGvaS28jHWQJBCulZP%2FkQPCeUavhJERI4S%2BbzuZvFlXe6VtvDTWw%3D%3D; JSESSIONID=""; __a=77707143.1572003017..1572003017.30.1.30.30; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1572448104"
    }
    proxies = {
        'http':'121.226.188.233:9999'
    }

    html = requests.get(url, proxies = proxies,headers=headers1).json()

    if html['rescode'] == 5002: # 如果rescode等于5002，表示ip被识别，需要去boss直聘手动验证
        time.sleep(10) #等待十秒，给手动验证预留时间
        html = parse_url(url)
    return html


# 获取职位详情页的职位信息，写入csv文件中
def insert_csv(positions,cityCode,cityName):
    file = "job_" + cityName + "1.csv"
    with open(file,'a') as f:
        head = ['城市','关键字', '薪资', '公司', '经验要求', '教育背景']
        f_csv = csv.writer(f)
        f_csv.writerow(head) # 先将标题行写进csv
        # 遍历所有职位和页面，拼接成网址获取json数据来分析
        for position in positions:
            for page in range(1,100):
                url = "https://www.zhipin.com/mobile/jobs.json?page={}&city={}&query={}".format(page,cityCode,position)
                # print(m)
                position_list = parse_url(url)
                print(position_list)
                if 'html' in position_list:
                    s = position_list['html']
                    m = re.findall(r'<li(.*?)/li>', s, re.S)
                    for k in m:
                        inf = re.search(r'salary">(.*?)<.*?name">(.*?)</.*?<em.*?<em>(.*?)</em><em>(.*?)</em>',k,re.S)
                        salary = inf.group(1)
                        company = inf.group(2)
                        experience = inf.group(3)
                        education = inf.group(4)
                        # print(salary,company,experience,education)
                        job = [cityName,position,salary,company,experience,education]
                        f_csv.writerow(job)
                if 'hasMore' in position_list:
                    if not position_list['hasMore']: #如果hasMore的值为false，则这一职位的信息已经遍历完
                        break

def main(hotcity,position):
    # for hot_city in cityList:
    insert_csv(position,hotcity[0],hotcity[1])
    print("city" + hotcity[1] + "is count over")


if __name__ == '__main__':
    proxies = {
        "http":"http://27.152.90.11:9999"
    }
    pool = Pool(5) # 5个线程同时进行，提高效率
    # 分析城市信息，这里只选取了几个热门城市
    city_url = "https://www.zhipin.com/wapi/zpCommon/data/city.json"
    city_html = requests.get(city_url,proxies = proxies).json()
    # print(city_html)
    if 'zpData' in city_html:
        hotCity = city_html['zpData']['hotCityList']
        city = []
        if hotCity:
            for i in range(1, len(hotCity)):
                code = hotCity[i]['code']
                name = hotCity[i]['name']
                city.append([code,name])
    # print(city)
        total_positions = getPositions()
        if total_positions:
            # 因为main函数有两个参数，而pool.map只能写一个参数，所以需要用到偏函数，先把一个参数固定下来
            partial_work = partial(main,position = total_positions)
            pool.map(partial_work,city)
        else:
            print("error")
    else:
        print("error")




