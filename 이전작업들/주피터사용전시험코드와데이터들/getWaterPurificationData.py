import os
import sys
import urllib.request
import json
import pandas as pd
import datetime

#광역정수장인증키
ServiceKey = 'TTnAEZu4veAnCYB24tpuD9DlMXhNL04FJPk7jMPXZq2cordqm0c0R1zZkS3FDH4jYSv2mxiPEMN2cPtWceTPwg%3D%3D'

#URL요청
def getRequestUrl(url):
    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            print("[%s] Url Request Successs" % datetime.datetime.now())
            return response.read().decode('utf-8')
    except Exception as e:
        print(e)
        print("[%s] Error for URL : %s" % (datetime.datetime.now(), url))
        return None


#######광역정수장 데이터 가져오기#######
#code : 광역정수장 코드
def getWaterPurificationItem(code):
    service_url = "http://opendata.kwater.or.kr/openapi-data/service/pubd/waterways/wdr/dailwater/list"
    
    parameters = "?_type=json"
    parameters += "&fcode=" + code
    parameters += "&stdt=2021-12-01&eddt=2021-12-01"
    parameters += "&serviceKey="+ ServiceKey

    url = service_url + parameters

    retData = getRequestUrl(url)

    if(retData == None):
        return None
    else:
        return json.loads(retData)


def getWaterPurificationService(code):
    jsonResult = []
    
    jsonData = getWaterPurificationItem(code)
    print(jsonData)
    if(jsonData['response']['header']['resultMsg']=='NORMAL SERVICE.'):
        if(jsonData['response']['body']['totalCount'] != 0):
            taste = jsonData['response']['body']['items']['item']['item1']
            smell = jsonData['response']['body']['items']['item']['item2']
            color = jsonData['response']['body']['items']['item']['item3']
            ph = jsonData['response']['body']['items']['item']['item4']
            ntu = jsonData['response']['body']['items']['item']['item5']
            chlorine = jsonData['response']['body']['items']['item']['item6']

            jsonResult.append({'맛': taste, '냄새': smell, '색도': color, 'pH': ph, '탁도': ntu, '잔류염소': chlorine})

        else:
            print("데이터가 없습니다.")
            return None

    print(jsonResult)    
    return jsonResult

#####삭제
#정수장이름+코드 가져오기
def getCode():
    name_list = []  #정수장 이름+코드 모두 저장
    service_url = "http://opendata.kwater.or.kr/openapi-data/service/pubd/waterways/wdr/waterfltplt/list"

    service_url += "?_type=json&serviceKey=" + ServiceKey
    service_url += "&numOfRows=50&pageNo=1"

    retData = getRequestUrl(service_url)
    jsonData = json.loads(retData)

    if(jsonData['response']['header']['resultMsg']=='NORMAL SERVICE.'):
        for data in jsonData['response']['body']['items']['item']:
            #정수장코드, 정수장이름
            code = data['fltplt']
            name = data['fltpltnm']

            name_list.append({'code': code, 'name': name})


    return name_list


#####수정
#지역명(name)으로 정수장 코드 반환
def findCode(name):
    dic = {"수도권":["A005","A020","A028","A038","A040","A041","A051","A056","A064","A090"],
           "강원도":["A039","A072"],
           "충청북도":["A061","A063"],
           "충청남도":["A007","A015","A030","A037","A042","A060"],
           "전라북도":["A004","A014","A023","A033","A036"],
           "전라남도":["A018","A021","A029","A065","A071"],
           "경상북도":["A002","A012","A055","A069"],
           "경상남도":["A013","A026","A027","A034","A045","A047"],
           "울산광역시":["A050","A057"]}
    return dic[name]
    
            


def main():
    jsonResult = []
    code = []
    name = input('지역 입력>')  #지역명 입력
    code = findCode(name)       #지역명 -> 코드로 변경 후 저장
    print(code)

    for c in code:
        jsonResult.append(getWaterPurificationService(c))


    #데이터가 있으면 저장
    if (jsonResult != None):        
        with open('C:/수업/4학년2학기/데이터크롤링/기말프로젝트/%s.json' % (name), 'w', encoding = 'utf8') as outfile:
            jsonFile = json.dumps(jsonResult, indent=4, sort_keys = True, ensure_ascii = False)
            outfile.write(jsonFile)
            print("저장 완료")


if __name__ == '__main__':
    main()
