# 페이지랭크, pheromone과 date를 정렬하여 키워드셋 제목 아이디와 함께 pagerank 컬력센에 저장
# 키워드 별로 최신2개, 최고 점수 5개, 랜덤 2개의 링크를 묶음 저장(new1 ~ new2, top1 ~ top5, ran1 ~ ran2)
# 입력값 : pagerank(대표키워드)
# 출력 : {'code' : 100, 'msg' : "True"}


# -*- coding: utf8 -*-
import pymongo
import operator
import time
import random
import json

connection = pymongo.MongoClient("localhost",27017)
db = connection.Health_One
linkc = db.link
keywordc = db.keyword
scorec = db.score
pagerankc = db.pagerank

def pagerank(keyword_title):
    try:
        # keyword_title을 받아 keyword_title_id를 찾음
        keyword_data = keywordc.find_one({"keyword_title":keyword_title})
        category = keyword_data["category"]
        scope_list = keyword_data['scope_list']

        # keyword_title_id에 해당하는 링크들을 찾음
        link_data = linkc.find({"keyword_title":keyword_title})

        # 정렬을 위한 딕셔너리
        link_pheromone_date = {}

        # link_pheromone_date딕셔너리에 찾은 링크의 _id를 키값으로 mktime(date_split), pheromone을 저장
        for data in link_data:

            date_split = data["date"].split("-")

            link_pheromone_date[data["_id"]] = [time.mktime((int(date_split[0]),int(date_split[1]),int(date_split[2]),0,0,0,0,0,0))]
            link_pheromone_date[data["_id"]].append(data["pheromone"])

        # 딕셔너리를 mktime(date_split) 기준으로 정렬
        link_pheromone_date = sorted(link_pheromone_date.items(), key=operator.itemgetter(1), reverse=True)

        # 해당 분류가 pagerank컬렉션에 이미 존재하면 삭제 -> 최신 rank 업데이트
        pagerankc.remove({"keyword_title":keyword_title})

        # pagerank 컬렉션 생성
        pagerankc.insert({"keyword_title":keyword_title, "category":category, "scope_list":scope_list})
        
        # 변수명을 위한 정의
        no = 1

        try:
            # pagerank 컬렉션에 new1 ~ new2 저장
            for data in link_pheromone_date:
                if no <= 2:
                    pagerankc.update({"keyword_title":keyword_title},{"$set":{"new" + str(no) + "_id":data[0]}})
                
                # top1 ~ top5 저장을 위한 순서 재배치
                [data][0][1].reverse()

                no += 1

            # new1 ~ new2 제외
            del(link_pheromone_date[0:2])

            # 딕셔너리를 pheromone 기준으로 정렬
            link_pheromone_date = sorted(link_pheromone_date, key=operator.itemgetter(1), reverse=True)

            # 변수명을 위한 정의 
            no = 1

            # pagerank 컬렉션에 top1 ~ top5 저장
            for data in link_pheromone_date:
                if no <= 5:
                    pagerankc.update({"keyword_title":keyword_title},{"$set":{"top" + str(no) + "_id":data[0]}})

                no += 1

            # top1 ~ top5 제외
            del(link_pheromone_date[0:5])

            # pagerank 컬렉션에 ran1 ~ ran2 저장
            for n in range(0,2):
                ran = random.randint(0,len(link_pheromone_date)-1)

                pagerankc.update({"keyword_title":keyword_title},{"$set":{"ran" + str(n+1) + "_id":link_pheromone_date[ran][0]}})

            print(json.dumps({'code' : 100, 'msg' : "True"},ensure_ascii=False))
            return json.dumps({'code' : 100, 'msg' : "True"},ensure_ascii=False)

        except:
            print(json.dumps({'code' : 101, 'msg' : "No link", 'keyword_title' : keyword_title},ensure_ascii=False))
            #return {'code' : 101, 'msg' : "No link", 'keyword_title' : keyword_title}

    except:
        print(json.dumps({'code' : 1, 'msg' : "False", 'keyword_title' : keyword_title},ensure_ascii=False))
        #return {'code' : 1, 'msg' : "False", 'keyword_title' : keyword_title}

if __name__=='__main__':
    for data in keywordc.find():
        pagerank(data["keyword_title"])
