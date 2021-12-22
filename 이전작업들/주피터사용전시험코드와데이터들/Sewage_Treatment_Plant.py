import os
import sys
import urllib.request
import datetime
import time
import json
import pandas as pd

# 인증키
ServiceKey = "MEvxGMhjpntYNY%2Fp5Riqo6cQx3uqhAXzVzsxv5AR%2BmLmdWits8IgvaiEDYBkYmsIlf2ixPUmOwbETtIIjb%2ByYQ%3D%3D"

#[CODE 1]
# URL에서 데이터 가져오기
def getRequestUrl(url):
    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            print("[%s] Url Request Success" % datetime.datetime.now())
            return response.read().decode('utf-8')
    except Exception as e:
        print(e)
        print("[%s] Error for URL: %s" % (datetime.datetime.now(), url))
        return None

#---------------------------------시설 정보-------------------------------------
#[CODE 2]
# 시설 정보 가져오기
def getFacility():
    # URL 만들기
    service_url = "http://opendata.kwater.or.kr/openapi-data/service/pubd/sewerage/waterQuality/fcltylist/codelist"
    parameters = "?serviceKey=" + ServiceKey
    parameters += "&pageNo=1"
    parameters += "&numOfRows=50"
    parameters += "&_type=json"
    url = service_url + parameters

    retData = getRequestUrl(url) #[CODE 1]

    # URL로부터 받은 데이터를 반환
    if (retData == None):
        return None
    else:
        return json.loads(retData)

#[CODE 3]
# 시설 정보 표시하기
def showFacility():
    jsonResult = [] # 저장할 데이터의 변수를 미리 지정

    jsonData = getFacility()
    if (jsonData['response']['header']['resultCode'] == '00'): # 데이터가 올바른 경우
        if (jsonData['response']['body']['totalCount'] != 0): # 데이터가 있을 경우
            for data in jsonData['response']['body']['items']['item']:
                loccd = data['loccd'] # 하수처리장 코드
                locnm = data['locnm'] # 하수처리장 이름
                jsonResult.append({loccd: locnm})
        else:
            print("데이터가 없습니다.")
            return None
    else:
        print("데이터가 보내지지 않았습니다.")
        return None

    # 하수처리장 목록 출력
    for item in jsonResult:
       print(item)

#---------------------------------수질 정보-------------------------------------
#[CODE 4]
# 일자별 수질 정보 가져오기
def getDailyWaterQuality(stDt, edDt, loccd):
    # URL 만들기
    service_url = "http://opendata.kwater.or.kr/openapi-data/service/pubd/sewerage/waterQuality/day/list"
    parameters = "?serviceKey=" + ServiceKey
    parameters += "&pageNo=1"
    parameters += "&numOfRows=1000"
    parameters += "&stDt=" + stDt
    parameters += "&edDt=" + edDt
    parameters += "&loccd=" + loccd
    parameters += "&_type=json"
    url = service_url + parameters

    retData = getRequestUrl(url) #[CODE 1]

    # URL로부터 받은 데이터를 반환
    if (retData == None):
        return None
    else:
        return json.loads(retData)

#[CODE 5]
# 일자별 수질 정보를 JSON 형태로 저장
def getDailyWaterQualityJson(stDt, edDt, loccd):
    jsonResult = [] # 저장할 데이터의 변수를 미리 지정

    jsonData = getDailyWaterQuality(stDt, edDt, loccd) #[CODE 4]
    if (jsonData['response']['header']['resultCode'] == '00'): # 데이터가 올바른 경우
        if (jsonData['response']['body']['totalCount'] != 0): # 데이터가 있을 경우
            for data in jsonData['response']['body']['items']['item']:
                bBac = data['bBac']
                bBod = data['bBod']
                bCod = data['bCod']
                bSs = data['bSs']
                bTn = data['bTn']
                bTp = data['bTp']
                bVal = data['bVal']
                loccd = data['loccd']
                locnm = data['locnm']
                temper = data['temper']
                uBac = data['uBac']
                uBod = data['uBod']
                uCod = data['uCod']
                uSs = data['uSs']
                uTn = data['uTn']
                uTp = data['uTp']
                uVal = data['uVal']
                weather = data['weather']
                wqdt = data['wqdt']
                wtemper = data['wtemper']
                jsonResult.append({'하수도처리시설코드': loccd, '하수도처리시설명': locnm, '수질등록일자': wqdt, '날씨': weather, '기온': temper, '수온': wtemper, '유입수BOD(mg/L)': uBod, '유입수COD(mg/L)': uCod, '유입수SS(mg/L)': uSs, '유입수TN(mg/L)': uTn, '유입수TP(mg/L)': uTp, '유입수대장균수(개/ml)': uBac, '유입량(m3/d)': uVal, '방류수BOD(mg/L)': bBod, '방류수COD(mg/L)': bCod, '방류수SS(mg/L)': bSs, '방류수TN(mg/L)': bTn, '방류수TP(mg/L)': bTp, '방류수대장균수(개/ml)': bBac, '방류량(m3/d)': bVal})
        else:
            print("데이터가 없습니다.")
            return None
    else:
        print("데이터가 보내지지 않았습니다.")
        return None
    return jsonResult

#[CODE 0]
# main
def main():
    jsonResult = []
    
    showFacility() #[CODE 3]
    # 코드, 시작과 끝 날짜를 입력
    code = input("하수처리시설 코드를 입력하세요>>")
    startDate = input("시작 날짜를 입력하세요(yyyy-MM-dd)>>")
    endDate = input("끝 날짜를 입력하세요(yyyy-MM-dd)>>")
    jsonResult = getDailyWaterQualityJson(startDate, endDate, code) #[CODE 5]

    # JSON 정보가 유효할 경우 저장
    if (jsonResult != None):
        with open('./%s_%s_%s.json' % (code, startDate, endDate), 'w', encoding = 'utf-8') as outfile:
            jsonFile = json.dumps(jsonResult, indent = 4, sort_keys = True, ensure_ascii = False)
            outfile.write(jsonFile)
            print("Saved")

if __name__ == '__main__':
    main()
