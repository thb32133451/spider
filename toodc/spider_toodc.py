#!/root/anaconda3/bin/python
# coding=utf-8

import requests
import json
import time
import pandas as pd
import random
from pprint import pprint

def getCityCode():
    cityList = set()
    url = 'https://www.toodc.cn/'
    result = requests.get(url).text
    result = result[result.find('<ul style="display:none;" data-v-53537a55>') : result.find('</ul>', result.find('<ul style="display:none;" data-v-53537a55>'))]
    # result = result[result.find('<ul style="display:;" data-v-53537a55>') : result.find('</ul>', result.find('<ul style="display:;" data-v-53537a55>'))]
    while result.find('<li data-v-53537a55><a href="/list/') > 0:
        cityCode = result[result.find('<li data-v-53537a55><a href="/list/')+35 : result.find('" target="_blank"', result.find('<li data-v-53537a55><a href="/list/'))]
        if '/' in cityCode:
            cityCode = cityCode[:cityCode.find('/')]
        result = result[result.find('" target="_blank"', result.find('<li data-v-53537a55><a href="/list/')):]
        if len(cityCode) > 0 and cityCode[0] == 'c':
            cityList.add(cityCode.replace('c', ''))
            # print(cityCode)
    return cityList

def getAllStringFromList(l):
    s = ''
    for i in l:
        s += (str(i) + '|')
    return s

def searchPageInfo(pageIndex, pageSize, cityCode):
    urls = 'https://www.toodc.cn/ns/list/search'
    params = {
        'pageIndex': pageIndex,
        'pageSize': pageSize,
        'cityCode': cityCode,
    }
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }

    response = requests.get(urls, params=params, headers=headers)
    if response.status_code == 200:
        result = json.loads(response.content)
        # pprint(result)
        return result['data']['rows'], result['data']['pageCount']
    else:
        return -1, -1


def getWarehouseIndex(projectId):
    urls = 'https://www.toodc.cn/project/detail/' + str(projectId)
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }
    try:
        response = requests.get(urls, headers=headers)
    except:
        print('error@%s'%projectId)
        return '',''
    if response.status_code == 200:
        result = str(response.text)
        recommendCount = result[result.find('近30天推荐数</p> <p data-v-5efd96fd><span data-v-5efd96fd>')+53 : result.find('</span>次', result.find('近30天推荐数</p> <p data-v-5efd96fd><span data-v-5efd96fd>'))]
        lookCount = result[result.find('近30天带看数</p> <p data-v-5efd96fd><span data-v-5efd96fd>')+53 : result.find('</span>次', result.find('近30天带看数</p> <p data-v-5efd96fd><span data-v-5efd96fd>'))]
        return recommendCount, lookCount
    else:
        return '',''


def getCityWarehouseInfo(cityCode):
    currentPageIndex = 1
    pageSize = 10
    info = pd.DataFrame(columns=['projectId', 'projectName', 'id', '标题', '副标题', '租金（元/平/天）', '面积', '地址', '特殊标签', '适用用途', '近30天推荐数', '近30天带看数'])

    while True:
        data, pageCount = searchPageInfo(currentPageIndex, pageSize, cityCode)
        print('%s -------->  %s/%s' % (cityCode, currentPageIndex, pageCount))
        if data != -1:
            for warehouse in data:
                cityShortName = warehouse['cityShortName']
                recommendCount, lookCount = getWarehouseIndex(warehouse['projectId'])
                warehouseInfo = pd.DataFrame(
                    {
                    'projectId' : warehouse['projectId'],
                    'projectName' : warehouse['projectName'],
                    'id' : warehouse['id'],
                    '标题' : warehouse['chiefSlogan'],
                    '副标题' : getAllStringFromList(warehouse['advTags']),
                    '租金（元/平/天）' : warehouse['precisePrice'],
                    '面积' : warehouse['totalArea'],
                    '地址' : warehouse['extendDatas']['position'],
                    '特殊标签' : getAllStringFromList(warehouse['extendDatas']['spec']),
                    '适用用途' : getAllStringFromList(warehouse['projectUseages']),
                    '近30天推荐数' : recommendCount,
                    '近30天带看数' : lookCount
                    },
                    index=['0'])
                # pprint(warehouseInfo)
                info = info.append(warehouseInfo, ignore_index=True)
        if pageCount == currentPageIndex or pageCount == None:
            break
        currentPageIndex += 1
        time.sleep(random.randint(1, 2))
        # time.sleep(1)
    info.to_csv('./data/' + cityShortName + '_' + cityCode + '_data.csv', encoding='utf-8')


def main():
    for city in getCityCode():
        print(city)
        getCityWarehouseInfo(city)


if __name__ == '__main__':
    main()

