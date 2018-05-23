from pymongo import MongoClient
import pymongo
import string
import csv
import pickle
import re
import sys
import urllib.request
from data_standard import modify_filed_name
from index import database_config,questions_filename,answers_filename,tags_filename,django_tags_filename
import math
import time
from utils.mongodb_utils import get_connection

def get_collectoin_all_data(conn, collection):
    db_collection = conn[collection]
    return db_collection.find()

#生成和django有关的django_answer,django_question数据集,新增tag字段，存到数据库中
class django_tags:
    def __init__(self):
        pass

    def get_connection_mongodb(self,config):
        connect = MongoClient(config['ip'], config['port'])
        return connect[config['dbName']]

  #在Tags.csv中筛选出和django有关的tag,生成数据集django_tags存到数据库中
    def store_db_collection(self,db,filename, collection_name):
        db_collection = db[collection_name]
        row_sum = 0
        pattern = re.compile("(.*?)django(.*?)")
        #读取Tags.csv
        with open(filename, 'r', encoding='utf-8', errors="replace") as fin:
            reader = csv.reader(fin)
            header = None
            cnt = 0
            objs = []
            #row csv文件中的一行
            for row in reader:
                if cnt % 10000 is 0:
                    print('insert into %s: %d/%d' % (collection_name, cnt, row_sum))
                cnt += 1
                if header is None:
                    header = row
                else:
                    obj = {}
                    for i in range(0, len(header)):
                        obj[header[i]] =row[i]
                    has_django_tag=pattern.match(obj["Tag"])
                    if has_django_tag:
                        objs.append(obj)
            db_collection.insert(objs)
            fin.close()
            print('%s (collection_name) has done')


    #根据Tags.csv文件中的Tag和问题的Id（对应answer的ParentID）,在Answer.csv中筛选出django有关的Answer，
    #在Question.csv中筛选出django有关的Question，
    #存在mongodb数据库django_answers这个数据集中
    def store_db_django_answers(self,db,collection_name,key,filename):
        db_collection = db[collection_name]
        row_sum = 0
        django_tags_id_list = {}
        django_id_list=[]
        django_answer_list=[]
        django_question_list=[]
        with open(django_tags_filename, 'r', encoding='utf-8', errors="replace") as fin:
            reader = csv.reader(fin)
            header = None
            cnt = 0
            count=0
            for row in reader:
                if cnt % 10000 is 0:
                    print('has read data %s: %d/%d' % (collection_name, cnt, row_sum))
                cnt += 1
                if header is None:
                    header = row
                else:
                    obj = {}
                    for i in range(0, len(header)):
                        obj[header[i]] =row[i]
                    django_id_list.append(obj["Id"])
                    django_tags_id_list[obj["Id"]]=obj["Tag"]
            fin.close()

        with open(filename, 'r', encoding='utf-8', errors="replace") as fin:
            reader = csv.reader(fin)
            header = None
            cnt = 0
            count_test=0
            for row in reader:
                if (cnt % 1000 is 0 and cnt!=0):
                    print('insert into %s: %d/%d' % (collection_name, cnt, row_sum))
                if header is None:
                    header = row
                else:
                    obj = {}
                    for i in range(0, len(header)):
                        obj[header[i]] =row[i]
                    if obj[key]in django_id_list:
                        obj["Tag"]=django_tags_id_list[obj["Id"]]
                        if filename==answers_filename:
                            django_answer_list.append(obj)
                        if filename==questions_filename:
                            django_question_list.append(obj)
                        cnt += 1

            if filename==answers_filename:
                db_collection.insert(django_answer_list)
            if filename==questions_filename:
                db_collection.insert(django_question_list)
            fin.close()
        print('has done')


if __name__ == '__main__':
    add_filed="Tag"
    filter_filed="ParentId"
    filter="Id"
    add_filed=["Title","QuestionBody"]
    django_tags=django_tags()
    db =get_connection()
    # django_tags.store_db_collection(db, tags_filename , 'django_tags')
    # django_tags.store_db_django_answers(db,'django_answers',"ParentId",answers_filename)
    # django_tags.append_tag_field_indb(db,'django_answers',add_filed,filter_filed,filter)
    # django_tags.store_db_django_answers(db,'django_questions',"Id",questions_filename)
    # django_tags.append_tag_field_indb(db,'django_answers_standard',add_filed,filter_filed,filter)
    # old_filedname_list=["Answer_Text","Answer_Link","Answer_Code","Answer_Id","Answewr_Body","Question_Title"]
    old_filedname_list=["AnswewrBody"]
    # new_filedname_list=["AnswerText","AnswerLink","AnswerCode","AnswerId","AnswerBody","QuestionTitle"]
    new_filedname_list=["AnswerBody"]
    modify_filed_name(db,"django_answers_keyword_tfidf",old_filedname_list,new_filedname_list)