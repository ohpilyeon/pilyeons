import os
import sys
import urllib.request
import json
import pandas as pd
import datetime

#인증키
ServiceKey = 'PgdnR4cgw6WwmfyR7rqzzBcJPu3rx3LPtinOu4hHP5B9o2oiJ6alrNDnOvcqdBmUQKgQxFW1WGDnEMPFh%2B87Zw%3D%3D'

#[CODE 1]
#URL Request
def getRequestUrl(url):
    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200: #연결 성공
            print("[%s] URL Request Success" % datetime.datetime.now())
            return response.read().decode('utf-8')
    except Exception as e: #연결 실패
        print(e)
        print("[%s] Error for URL: %s" % (datetime.datetime.now(), url))
        return None

#===========================지자체 정보===========================
#[CODE 2]
#지자체 정보 가져오기
def getWaterSgc():
    #URL 만들기
    service_url = 'http://opendata.kwater.or.kr/openapi-data/service/pubd/waterinfos/waterquality/watersgcl/codelist'
    parameters = '?serviceKey=' + ServiceKey
    parameters += '&%EC%97%86%EC%9D%8C=NULL'
    parameters += '&_type=json'
    url = service_url + parameters

    retData = getRequestUrl(url) #[CODE 1]

    #받은 데이터가 존재하는지 검사
    if (retData != None and json.loads(retData)['response']['header']['resultCode'] == '00'):
        return json.loads(retData)
    else: #API 서버의 일일 호출량을 초과했을 경우 로컬 json 파일을 불러온다.
        f = open('./json/sgcList.json', 'r', encoding = 'utf-8')
        retData = f.read()
        f.close()
        return json.loads(retData)

#[CODE 3]
#지자체 목록 표시하기
def showWaterSgcList():
    jsonData = getWaterSgc() #[CODE 2]

    #받은 데이터가 올바른지 검사하고 목록 표시
    if (jsonData['response']['header']['resultCode'] == '00'):
        for data in jsonData['response']['body']['items']['item']:
            print(data['sgcnm'])
    else:
        return None

#[CODE 4]
#지자체 코드로 변환하기
def sgcNameToCode(sgcName):
    name_list = []
    jsonData = getWaterSgc() #[CODE 2]

    #받은 데이터가 올바른지 검사하고 데이터를 저장하기
    if (jsonData['response']['header']['resultCode'] == '00'):
        for data in jsonData['response']['body']['items']['item']:
            code = data['sgccd'] #코드
            name = data['sgcnm'] #이름
            name_list.append({'sgccd': code, 'sgcnm': name})
    else:
        return None

    #지자체 이름이 유효한 경우
    for lst in name_list:
        if sgcName in lst['sgcnm']:
            return str(lst['sgccd']) #String 형식으로 변환해야 URL에 덧붙일 수 있다.
    return None

#===========================정수장 정보===========================
#[CODE 5]
#정수장 정보 가져오기
def getWaterSite(sgcCode):
    #URL 만들기
    service_url = 'http://opendata.kwater.or.kr/openapi-data/service/pubd/waterinfos/waterquality/watersite/codelist'
    parameters = '?serviceKey=' + ServiceKey
    parameters += '&sgccd=' + sgcCode
    parameters += '&_type=json'
    url = service_url + parameters

    retData = getRequestUrl(url) #[CODE 1]

    #받은 데이터가 존재하는지 검사
    if (retData != None and json.loads(retData)['response']['header']['resultCode'] == '00'):
        return json.loads(retData)
    else: #API 서버의 일일 호출량을 초과했을 경우 로컬 json 파일을 불러온다.
        f = open('./json/%s.json' % (sgcCode), 'r', encoding = 'utf-8')
        retData = f.read()
        f.close()
        return json.loads(retData)

#[CODE 6]
#정수장 목록 표시하기
def showWaterSiteList(sgcCode):
    jsonData = getWaterSite(sgcCode) #[CODE 5]

    #받은 데이터가 올바른지 검사하고 목록 표시
    if (jsonData['response']['header']['resultCode'] == '00'):
        if (type(jsonData['response']['body']['items']['item']) is dict): #정수장이 1개일 경우
            print(jsonData['response']['body']['items']['item']['sitenm'])
        else: #정수장이 여러 개인 경우(type: list)
            for data in jsonData['response']['body']['items']['item']:
                print(data['sitenm'])
    else:
        return None
        

#[CODE 7]
#정수장 코드로 변환하기
def siteNameToCode(sgcCode, siteName):
    name_list = []
    jsonData = getWaterSite(sgcCode) #[CODE 5]

    #받은 데이터가 올바른지 검사하고 데이터를 저장하기
    if (jsonData['response']['header']['resultCode'] == '00'):
        if (type(jsonData['response']['body']['items']['item']) is dict): #정수장이 1개일 경우
            code = jsonData['response']['body']['items']['item']['sitecd'] #코드
            name = jsonData['response']['body']['items']['item']['sitenm'] #이름
            name_list.append({'sitecd': code, 'sitenm': name})
        else: #정수장이 여러 개인 경우(type: list)
            for data in jsonData['response']['body']['items']['item']:
                code = data['sitecd'] #코드
                name = data['sitenm'] #이름
                name_list.append({'sitecd': code, 'sitenm': name})
    else:
        return None

    #정수장 이름이 유효한 경우
    for lst in name_list:
        if siteName in lst['sitenm']:
            return str(lst['sitecd']) #String 형식으로 변환해야 URL에 덧붙일 수 있다.
    return None

#============================수질 정보===========================
#[CODE 8]
#일일 수질정보
def getDayWater(sgcCode, siteCode, startDate, endDate):
    jsonResult = []
    #URL 만들기
    service_url = 'http://opendata.kwater.or.kr/openapi-data/service/pubd/waterinfos/waterquality/daywater/list'
    parameters = '?serviceKey=' + ServiceKey
    parameters += '&sgccd=' + sgcCode
    parameters += '&sitecd=' + siteCode
    parameters += '&stdt=' + startDate
    parameters += '&eddt=' + endDate
    parameters += '&numOfRows=100' #한 번에 최대 100개의 항목을 보여주기
    parameters += '&pageNo=1'
    parameters += '&_type=json'
    url = service_url + parameters

    retData = getRequestUrl(url) #[CODE 1]

    #받은 데이터가 존재하는지 검사
    if (retData == None):
        return None
    else:
        jsonData = json.loads(retData)

    #받은 데이터가 올바른지 검사하고 데이터를 저장하기
    if (jsonData['response']['header']['resultCode'] == '00'):
        if (type(jsonData['response']['body']['items']['item']) is dict): #결과가 1개인 경우
            sgcnm = jsonData['response']['body']['items']['item']['sgcnm']
            sitenm = jsonData['response']['body']['items']['item']['sitenm']
            cltdt = jsonData['response']['body']['items']['item']['cltdt']
            data1 = jsonData['response']['body']['items']['item']['data1']
            data2 = jsonData['response']['body']['items']['item']['data2']
            data3 = jsonData['response']['body']['items']['item']['data3']
            data4 = jsonData['response']['body']['items']['item']['data4']
            data5 = jsonData['response']['body']['items']['item']['data5']
            data6 = jsonData['response']['body']['items']['item']['data6']
            jsonResult.append({'지자체명': sgcnm, '정수장명': sitenm, '측정일자': cltdt, '맛': data1, '냄새': data2, '색도(도)': data3, 'pH(-)': data4, '탁도(NTU)': data5, '잔류염소(mg/L)': data6})
        else: #결과가 여러 개인 경우
            for data in jsonData['response']['body']['items']['item']:
                sgcnm = data['sgcnm']
                sitenm = data['sitenm']
                cltdt = data['cltdt']
                data1 = data['data1']
                data2 = data['data2']
                data3 = data['data3']
                data4 = data['data4']
                data5 = data['data5']
                data6 = data['data6']
                jsonResult.append({'지자체명': sgcnm, '정수장명': sitenm, '측정일자': cltdt, '맛': data1, '냄새': data2, '색도(도)': data3, 'pH(-)': data4, '탁도(NTU)': data5, '잔류염소(mg/L)': data6})
    else:
        return None

    return jsonResult

#[CODE 9]
#주간 수질정보
def getWeekWater(sgcCode, siteCode, startDate, endDate):
    jsonResult = []
    #URL 만들기
    service_url = 'http://opendata.kwater.or.kr/openapi-data/service/pubd/waterinfos/waterquality/weekwater/list'
    parameters = '?serviceKey=' + ServiceKey
    parameters += '&sgccd=' + sgcCode
    parameters += '&sitecd=' + siteCode
    parameters += '&stdt=' + startDate
    parameters += '&eddt=' + endDate
    parameters += '&numOfRows=100' #한 번에 최대 100개의 항목을 보여주기
    parameters += '&pageNo=1'
    parameters += '&_type=json'
    url = service_url + parameters

    retData = getRequestUrl(url) #[CODE 1]

    #받은 데이터가 존재하는지 검사
    if (retData == None):
        return None
    else:
        jsonData = json.loads(retData)

    #받은 데이터가 올바른지 검사하고 데이터를 저장하기
    if (jsonData['response']['header']['resultCode'] == '00'):
        if (type(jsonData['response']['body']['items']['item']) is dict): #결과가 1개인 경우
            sgcnm = jsonData['response']['body']['items']['item']['sgcnm']
            sitenm = jsonData['response']['body']['items']['item']['sitenm']
            cltdt = jsonData['response']['body']['items']['item']['cltdt']
            data1 = jsonData['response']['body']['items']['item']['data1']
            data2 = jsonData['response']['body']['items']['item']['data2']
            data3 = jsonData['response']['body']['items']['item']['data3']
            data4 = jsonData['response']['body']['items']['item']['data4']
            data5 = jsonData['response']['body']['items']['item']['data5']
            data6 = jsonData['response']['body']['items']['item']['data6']
            data7 = jsonData['response']['body']['items']['item']['data7']
            jsonResult.append({'지자체명': sgcnm, '정수장명': sitenm, '측정일자': cltdt, '일반세균(CFU/mL)': data1, '총대장균군(/100mL)': data2, '대장균/분원성대장균(/100mL)': data3, '암모니아성질소(mg/L)': data4, '질산성질소(mg/L)': data5, '과망간산칼륨소비량(mg/L)': data6, '증발잔류물(mg/L)': data7})
        else: #결과가 여러 개인 경우
            for data in jsonData['response']['body']['items']['item']:
                sgcnm = data['sgcnm']
                sitenm = data['sitenm']
                cltdt = data['cltdt']
                data1 = data['data1']
                data2 = data['data2']
                data3 = data['data3']
                data4 = data['data4']
                data5 = data['data5']
                data6 = data['data6']
                data7 = data['data7']
                jsonResult.append({'지자체명': sgcnm, '정수장명': sitenm, '측정일자': cltdt, '일반세균(CFU/mL)': data1, '총대장균군(/100mL)': data2, '대장균/분원성대장균(/100mL)': data3, '암모니아성질소(mg/L)': data4, '질산성질소(mg/L)': data5, '과망간산칼륨소비량(mg/L)': data6, '증발잔류물(mg/L)': data7})
    else:
        return None

    return jsonResult

#[CODE 10]
#월간 수질정보
#59번 데이터는 2018년 1월부터 포함되었으며, 그 이전 기간까지 입력하면 저장이 되지 않을 수 있다.
def getMonthWater(sgcCode, siteCode, startDate, endDate):
    jsonResult = []
    #URL 만들기
    service_url = 'http://opendata.kwater.or.kr/openapi-data/service/pubd/waterinfos/waterquality/monthwater/list'
    parameters = '?serviceKey=' + ServiceKey
    parameters += '&sgccd=' + sgcCode
    parameters += '&sitecd=' + siteCode
    parameters += '&stdt=' + startDate
    parameters += '&eddt=' + endDate
    parameters += '&numOfRows=100' #한 번에 최대 100개의 항목을 보여주기
    parameters += '&pageNo=1'
    parameters += '&_type=json'
    url = service_url + parameters
    
    retData = getRequestUrl(url) #[CODE 1]

    #받은 데이터가 존재하는지 검사
    if (retData == None):
        return None
    else:
        jsonData = json.loads(retData)

    #받은 데이터가 올바른지 검사하고 데이터를 저장하기
    if (jsonData['response']['header']['resultCode'] == '00'):
        if (type(jsonData['response']['body']['items']['item']) is dict): #결과가 1개인 경우
            sgcnm = jsonData['response']['body']['items']['item']['sgcnm']
            sitenm = jsonData['response']['body']['items']['item']['sitenm']
            cltdt = jsonData['response']['body']['items']['item']['cltdt']
            data1 = jsonData['response']['body']['items']['item']['data1']
            data2 = jsonData['response']['body']['items']['item']['data2']
            data3 = jsonData['response']['body']['items']['item']['data3']
            data4 = jsonData['response']['body']['items']['item']['data4']
            data5 = jsonData['response']['body']['items']['item']['data5']
            data6 = jsonData['response']['body']['items']['item']['data6']
            data7 = jsonData['response']['body']['items']['item']['data7']
            data8 = jsonData['response']['body']['items']['item']['data8']
            data9 = jsonData['response']['body']['items']['item']['data9']
            data10 = jsonData['response']['body']['items']['item']['data10']
            data11 = jsonData['response']['body']['items']['item']['data11']
            data12 = jsonData['response']['body']['items']['item']['data12']
            data13 = jsonData['response']['body']['items']['item']['data13']
            data14 = jsonData['response']['body']['items']['item']['data14']
            data15 = jsonData['response']['body']['items']['item']['data15']
            data16 = jsonData['response']['body']['items']['item']['data16']
            data17 = jsonData['response']['body']['items']['item']['data17']
            data18 = jsonData['response']['body']['items']['item']['data18']
            data19 = jsonData['response']['body']['items']['item']['data19']
            data20 = jsonData['response']['body']['items']['item']['data20']
            data21 = jsonData['response']['body']['items']['item']['data21']
            data22 = jsonData['response']['body']['items']['item']['data22']
            data23 = jsonData['response']['body']['items']['item']['data23']
            data24 = jsonData['response']['body']['items']['item']['data24']
            data25 = jsonData['response']['body']['items']['item']['data25']
            data26 = jsonData['response']['body']['items']['item']['data26']
            data27 = jsonData['response']['body']['items']['item']['data27']
            data28 = jsonData['response']['body']['items']['item']['data28']
            data29 = jsonData['response']['body']['items']['item']['data29']
            data30 = jsonData['response']['body']['items']['item']['data30']
            data31 = jsonData['response']['body']['items']['item']['data31']
            data32 = jsonData['response']['body']['items']['item']['data32']
            data33 = jsonData['response']['body']['items']['item']['data33']
            data34 = jsonData['response']['body']['items']['item']['data34']
            data35 = jsonData['response']['body']['items']['item']['data35']
            data36 = jsonData['response']['body']['items']['item']['data36']
            data37 = jsonData['response']['body']['items']['item']['data37']
            data38 = jsonData['response']['body']['items']['item']['data38']
            data39 = jsonData['response']['body']['items']['item']['data39']
            data40 = jsonData['response']['body']['items']['item']['data40']
            data41 = jsonData['response']['body']['items']['item']['data41']
            data42 = jsonData['response']['body']['items']['item']['data42']
            data43 = jsonData['response']['body']['items']['item']['data43']
            data44 = jsonData['response']['body']['items']['item']['data44']
            data45 = jsonData['response']['body']['items']['item']['data45']
            data46 = jsonData['response']['body']['items']['item']['data46']
            data47 = jsonData['response']['body']['items']['item']['data47']
            data48 = jsonData['response']['body']['items']['item']['data48']
            data49 = jsonData['response']['body']['items']['item']['data49']
            data50 = jsonData['response']['body']['items']['item']['data50']
            data51 = jsonData['response']['body']['items']['item']['data51']
            data52 = jsonData['response']['body']['items']['item']['data52']
            data53 = jsonData['response']['body']['items']['item']['data53']
            data54 = jsonData['response']['body']['items']['item']['data54']
            data55 = jsonData['response']['body']['items']['item']['data55']
            data56 = jsonData['response']['body']['items']['item']['data56']
            data57 = jsonData['response']['body']['items']['item']['data57']
            data58 = jsonData['response']['body']['items']['item']['data58']
            data59 = jsonData['response']['body']['items']['item']['data59']
            jsonResult.append({'지자체명': sgcnm, '정수장명': sitenm, '측정일자': cltdt, '일반세균(CFU/mL)': data1, '총대장균군(/100mL)': data2, '대장균(E.coil) (/100mL)': data3, '납(Pb)(mg/L)': data4, '불소(F) (mg/L)': data5, '비소(mg/L)': data6, '셀레늄(Se) (mg/L)': data7, '수은(Hg) (mg/L)': data8, '시안(CN) (mg/L)': data9, '크롬(Cr) (mg/L)': data10, '암모니아성질소(mg/L)': data11, '질산성질소(mg/L)': data12, '보론(B) (mg/L)': data13, '카드뮴(Cd) (mg/L)': data14, '페놀(mg/L)': data15, '총트리할로메탄(THMs) (mg/L)': data16, '클로로포름(mg/L)': data17, '다이아지논(mg/L)': data18, '파라티온(mg/L)': data19, '페니트로티온(mg/L)': data20, '카바릴(mg/L)': data21, '1,1,1-트리클로로에탄(mg/L)': data22, '테트라클로로에틸렌(PCE) (mg/L)': data23, '트리클로로에틸렌(TCE) (mg/L)': data24, '디클로로메탄(mg/L)': data25, '벤젠(mg/L)': data26, '톨루엔(mg/L)': data27, '에틸벤젠(mg/L)': data28, '크실렌(mg/L)': data29, '1,1디클로로에틸렌(mg/L)': data30, '사염화탄소(mg/L)': data31, '1,2-디브로모-3-클로로프로판(mg/L)': data32, '잔류염소(mg/L)': data33, '클로랄하이드레이트(CH) (mg/L)': data34, '디브로모아세토니트릴(mg/L)': data35, '디클로로아세토니트릴(mg/L)': data36, '트리클로로아세토니트릴(mg/L)': data37, '할로아세틱에시드(HAAs) (mg/L)': data38, '경도(mg/L)': data39, '과망간산칼륨소비량(mg/L)': data40, '냄새(무취)': data41, '맛(무미)': data42, '구리(Cu) (mg/L)': data43, '색도(도) (mg/L)': data44, '세제(음이온계면활성제:ABS) (mg/L)': data45, '수소이온농도(pH)': data46, '아연(Zn) (mg/L)': data47, '염소이온(mg/L)': data48, '증발잔류물(Totalsolids) (mg/L)': data49, '철(Fe) (mg/L)': data50, '망간(Mn) (mg/L)': data51, '탁도(Turbidity) (NTU)': data52, '황산이온(mg/L)': data53, '알루미늄(Al) (mg/L)': data54, '브로모디클로로메탄(mg/L)': data55, '디브로모클로로메탄(mg/L)': data56, '1,4-다이옥산(mg/L)': data57, '포름알데히드(mg/L)': data58, '브롬산염(mg/L)': data59})
        else: #결과가 여러 개인 경우
            for data in jsonData['response']['body']['items']['item']:
                sgcnm = data['sgcnm']
                sitenm = data['sitenm']
                cltdt = data['cltdt']
                data1 = data['data1']
                data2 = data['data2']
                data3 = data['data3']
                data4 = data['data4']
                data5 = data['data5']
                data6 = data['data6']
                data7 = data['data7']
                data8 = data['data8']
                data9 = data['data9']
                data10 = data['data10']
                data11 = data['data11']
                data12 = data['data12']
                data13 = data['data13']
                data14 = data['data14']
                data15 = data['data15']
                data16 = data['data16']
                data17 = data['data17']
                data18 = data['data18']
                data19 = data['data19']
                data20 = data['data20']
                data21 = data['data21']
                data22 = data['data22']
                data23 = data['data23']
                data24 = data['data24']
                data25 = data['data25']
                data26 = data['data26']
                data27 = data['data27']
                data28 = data['data28']
                data29 = data['data29']
                data30 = data['data30']
                data31 = data['data31']
                data32 = data['data32']
                data33 = data['data33']
                data34 = data['data34']
                data35 = data['data35']
                data36 = data['data36']
                data37 = data['data37']
                data38 = data['data38']
                data39 = data['data39']
                data40 = data['data40']
                data41 = data['data41']
                data42 = data['data42']
                data43 = data['data43']
                data44 = data['data44']
                data45 = data['data45']
                data46 = data['data46']
                data47 = data['data47']
                data48 = data['data48']
                data49 = data['data49']
                data50 = data['data50']
                data51 = data['data51']
                data52 = data['data52']
                data53 = data['data53']
                data54 = data['data54']
                data55 = data['data55']
                data56 = data['data56']
                data57 = data['data57']
                data58 = data['data58']
                data59 = data['data59']
                jsonResult.append({'지자체명': sgcnm, '정수장명': sitenm, '측정일자': cltdt, '일반세균(CFU/mL)': data1, '총대장균군(/100mL)': data2, '대장균(E.coil) (/100mL)': data3, '납(Pb)(mg/L)': data4, '불소(F) (mg/L)': data5, '비소(mg/L)': data6, '셀레늄(Se) (mg/L)': data7, '수은(Hg) (mg/L)': data8, '시안(CN) (mg/L)': data9, '크롬(Cr) (mg/L)': data10, '암모니아성질소(mg/L)': data11, '질산성질소(mg/L)': data12, '보론(B) (mg/L)': data13, '카드뮴(Cd) (mg/L)': data14, '페놀(mg/L)': data15, '총트리할로메탄(THMs) (mg/L)': data16, '클로로포름(mg/L)': data17, '다이아지논(mg/L)': data18, '파라티온(mg/L)': data19, '페니트로티온(mg/L)': data20, '카바릴(mg/L)': data21, '1,1,1-트리클로로에탄(mg/L)': data22, '테트라클로로에틸렌(PCE) (mg/L)': data23, '트리클로로에틸렌(TCE) (mg/L)': data24, '디클로로메탄(mg/L)': data25, '벤젠(mg/L)': data26, '톨루엔(mg/L)': data27, '에틸벤젠(mg/L)': data28, '크실렌(mg/L)': data29, '1,1디클로로에틸렌(mg/L)': data30, '사염화탄소(mg/L)': data31, '1,2-디브로모-3-클로로프로판(mg/L)': data32, '잔류염소(mg/L)': data33, '클로랄하이드레이트(CH) (mg/L)': data34, '디브로모아세토니트릴(mg/L)': data35, '디클로로아세토니트릴(mg/L)': data36, '트리클로로아세토니트릴(mg/L)': data37, '할로아세틱에시드(HAAs) (mg/L)': data38, '경도(mg/L)': data39, '과망간산칼륨소비량(mg/L)': data40, '냄새(무취)': data41, '맛(무미)': data42, '구리(Cu) (mg/L)': data43, '색도(도) (mg/L)': data44, '세제(음이온계면활성제:ABS) (mg/L)': data45, '수소이온농도(pH)': data46, '아연(Zn) (mg/L)': data47, '염소이온(mg/L)': data48, '증발잔류물(Totalsolids) (mg/L)': data49, '철(Fe) (mg/L)': data50, '망간(Mn) (mg/L)': data51, '탁도(Turbidity) (NTU)': data52, '황산이온(mg/L)': data53, '알루미늄(Al) (mg/L)': data54, '브로모디클로로메탄(mg/L)': data55, '디브로모클로로메탄(mg/L)': data56, '1,4-다이옥산(mg/L)': data57, '포름알데히드(mg/L)': data58, '브롬산염(mg/L)': data59})
    else:
        return None

    return jsonResult

#[CODE 11]
#상수원수 수질정보
#2018년 이전에는 일부 정보가 누락될 수 있다.
def getMonthQtrWater(sgcCode, startDate, endDate):
    jsonResult = []
    #URL 만들기
    service_url = 'http://opendata.kwater.or.kr/openapi-data/service/pubd/waterinfos/waterquality/monthqtrwater/list'
    parameters = '?serviceKey=' + ServiceKey
    parameters += '&sgccd=' + sgcCode
    parameters += '&stdt=' + startDate
    parameters += '&eddt=' + endDate
    parameters += '&numOfRows=100' #한 번에 최대 100개의 항목을 보여주기
    parameters += '&pageNo=1'
    parameters += '&_type=json'
    url = service_url + parameters

    retData = getRequestUrl(url) #[CODE 1]

    #받은 데이터가 존재하는지 검사
    if (retData == None):
        return None
    else:
        jsonData = json.loads(retData)

    #받은 데이터가 올바른지 검사하고 데이터를 저장하기
    if (jsonData['response']['header']['resultCode'] == '00'):
        if (type(jsonData['response']['body']['items']['item']) is dict): #결과가 1개인 경우
            sgcnm = jsonData['response']['body']['items']['item']['sgcnm']
            sitenm = jsonData['response']['body']['items']['item']['sitenm']
            cltdt = jsonData['response']['body']['items']['item']['cltdt']
            data1 = jsonData['response']['body']['items']['item']['data1']
            data2 = jsonData['response']['body']['items']['item']['data2']
            data3 = jsonData['response']['body']['items']['item']['data3']
            data4 = jsonData['response']['body']['items']['item']['data4']
            data5 = jsonData['response']['body']['items']['item']['data5']
            data6 = jsonData['response']['body']['items']['item']['data6']
            jsonResult.append({'지자체명': sgcnm, '정수장명': sitenm, '측정일자': cltdt, '수소이온농도(pH)': data1, 'BOD(호소수:COD) (mg/L)': data2, '부유물질(SS) (mg/L)': data3, '용존산소량(DO) (mg/L)': data4, '총대장균군(균수/100mL)': data5, '분원성대장균군수(균수/100mL)': data6})
        else: #결과가 여러 개인 경우
            for data in jsonData['response']['body']['items']['item']:
                sgcnm = data['sgcnm']
                sitenm = data['sitenm']
                cltdt = data['cltdt']
                data1 = data['data1']
                data2 = data['data2']
                data3 = data['data3']
                data4 = data['data4']
                data5 = data['data5']
                data6 = data['data6']
                jsonResult.append({'지자체명': sgcnm, '정수장명': sitenm, '측정일자': cltdt, '수소이온농도(pH)': data1, 'BOD(호소수:COD) (mg/L)': data2, '부유물질(SS) (mg/L)': data3, '용존산소량(DO) (mg/L)': data4, '총대장균군(균수/100mL)': data5, '분원성대장균군수(균수/100mL)': data6})
    else:
        return None

    return jsonResult

#[CODE 0]
#main
def main():
    jsonResult = []
    showWaterSgcList() #[CODE 3]
    sgcName = input('지자체명을 입력하세요>>')
    sgcCode = sgcNameToCode(sgcName) #[CODE 4]
    showWaterSiteList(sgcCode) #[CODE 6]
    siteName = input('정수장명을 입력하세요>>')
    siteCode = siteNameToCode(sgcCode, siteName) #[CODE 7]

    #info_type: 저장할 파일 이름에 남기는 정보의 종류
    print('1. 일일 수질정보')
    print('2. 주간 수질정보')
    print('3. 월간 수질정보')
    print('4. 상수원수 수질정보')
    choice = input('원하는 정보를 선택하십시오>>')
    if (choice == '1'): #일일 수질정보
        startDate = input('시작 날짜(yyyyMMdd)>>')
        endDate = input('끝 날짜(yyyyMMdd)>>')
        info_type = '일일'
        jsonResult = getDayWater(sgcCode, siteCode, startDate, endDate) #[CODE 8]
    elif (choice == '2'): #주간 수질정보
        startDate = input('시작 날짜(yyyyMMdd)>>')
        endDate = input('끝 날짜(yyyyMMdd)>>')
        info_type = '주간'
        jsonResult = getWeekWater(sgcCode, siteCode, startDate, endDate) #[CODE 9]
    elif (choice == '3'): #월간 수질정보
        startDate = input('시작 날짜(yyyyMM)>>')
        endDate = input('끝 날짜(yyyyMM)>>')
        info_type = '월간'
        jsonResult = getMonthWater(sgcCode, siteCode, startDate, endDate) #[CODE 10]
    elif (choice == '4'): #상수원수 수질정보
        startDate = input('시작 날짜(yyyyMM)>>')
        endDate = input('끝 날짜(yyyyMM)>>')
        info_type = '상수원수'
        jsonResult = getMonthQtrWater(sgcCode, startDate, endDate) #[CODE 11]
    else:
        print('잘못 입력하였습니다')

    #데이터가 있으면 저장
    if (jsonResult != None):        
        with open('./%s_%s_%s_%s_%s.json' % (sgcName, siteName, startDate, endDate, info_type), 'w', encoding = 'utf8') as outfile:
            jsonFile = json.dumps(jsonResult, indent=4, sort_keys = True, ensure_ascii = False)
            outfile.write(jsonFile)
            print("Saved")

if __name__ == '__main__':
    main()
