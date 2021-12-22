from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import json
import re
#한글 글자수 세기위해서 re.findall()



#해야할거 -> 한글개수 세주는 함수짜기(완료) and br태그로 본문뽑기
#2-> 뽑은 ptag 또는 brtag 데이터에서 해당 데이터중
#필요한 문자열만 나두고 쓰레기 문자들 제거
#3-> 뽑은 문자열에서 필요데이터 뽑기

def countHangul(text):
    #텍스트로부터 한글을 읽는데, 단어를 개수로 셈(정규식사용)
    hanCount=len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+',text))
    return hanCount

def getTextFromLink(url):
    print(url)
    html=urllib.request.urlopen(url)
    soupNews = BeautifulSoup(html,'html.parser')
    #print(soupNews.prettify())
    tag_tbody = soupNews.find('tbody')

    #tag_br=soupNews.select_one("br").parent.get_text().strip()

    tag_p=soupNews.find_all("p")
    
    #print("\ntag_p")
    #print(tag_p)
    #print("\ntag_br")
    #print(tag_br)
    return tag_p

#p태그로 분리한 tag_p에서 일정개수 이상의 한글이 안나오면 본문이
#아니라고 판단하면 될듯 ex 한글개수30개보다 적다. 이러면 해당 데이터는 날리고
#이때 br태그로 다시 본문을 뽑아보고 그후에 다시한번 한글 확인후 날리면될드
#뉴스사이트들마다 같은 기사가 있는것을 확인했음.
#만약 이 두조건으로 검색안되는 뉴스본문은 날려도 다른 뉴스사이트 본문에서 같은
#내용을 다뤄서 상관이 없을듯 싶음.

#br태그값은 br태그 이전의 값을 추출해야함... 어떻게 하지?(부분완료)
#bs4에서 지원하는 함수를 아직 못찾음
#아예없으면 html 코드를 처음부터 읽다가 br태그 발견->앞의한글문자열 추출
#이런식으로 뽑으면 될듯하다.

#1차해결법 -> br태그에 나와있으면 그 상위 태그값을찾아감 .parent 이용
#해당글의 텍스트를 전체를 뽑아봄. -> 성공?인듯


def getTextFromBrTag(url):
    print(url)
    html=urllib.request.urlopen(url)
    soupNews = BeautifulSoup(html,'html.parser')
    #print(soupNews.prettify())
    tag_tbody = soupNews.find('tbody')

    tag_br=soupNews.select_one("br").parent.get_text().strip()

    #print("\ntag_br")
    #print(tag_br)
    return tag_br
    
def main():
    with open("C:/Users/pilye/Desktop/final_project/수돗물 음용률_naver_news.json",'r',encoding="UTF-8") as f:
        json_data = json.load(f)
    link_data=[]
    i=0
    for data in json_data:
        link_data.append(data['org_link'])
        print(data)
        i=i+1
        if i==15:
            break
    print('\nlinkdata===\n')
    print(link_data)
    result=[]
    url='https://www.siminilbo.co.kr/news/newsview.php?ncode=1160291781968047'
    for link in link_data:
        result_text=[]
        text_data=getTextFromLink(link)
        #text_data의 타입이 bs4 resultOjb라서 텍스트 변환에 문제있음.
        for t in text_data:
            print(t.text)
            count=countHangul(t.text)
            print(count)
            if count>10:
                result_text.append(t.text)
            print('\n')
        #result_text에 추가된 전체글을 다시 세본다.
        #->만약 전체글이 50단어 미만이면 br태그로 재검색
        #count = 0
        #for t in result_text:
            
        #count=countHangul(text_data)
        #print(count)
        #print('\n')
        result.append(result_text)
        #전체 글중에서 result안의 한글을 전부 세서 50개미만이라던가
        #특정 개수 이하면 br태그로 재검색하면 될듯.

    print("==============++++++++++++++++++++++++++====재확인용")
    for r in result:
        print(r)
        print('\n')
def textOut(preData,textResult):
    #json전처리필요
    with open('textOut', 'w', encoding='utf8') as outfile:
        #jsonFile = json.dumps(jsonResult,  indent=4, sort_keys=True,  ensure_ascii=False)
                        
        outfile.write(jsonFile)
if __name__=='__main__':
    main()
