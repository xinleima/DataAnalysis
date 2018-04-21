from pymongo import MongoClient
import pymongo
import string
import csv
import pickle
import re
import sys
import urllib.request
from index import database_config,questions_filename,answers_filename,tags_filename,django_tags_filename
import math
import time

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

    #根据filter在数据库中批量增加字段
    #add_filed 在数据库中增加的字段 类型为string
    #filter_filed在数据库中过滤的字段 类型为string
    #filter 过滤条件的名称，对应于数据库中过滤字段，csv文件中字段 类型为string
    def append_tag_field_indb(self,db,collection_name,add_filed,filter_filed,filter):
        db_collection = db[collection_name]
        row_sum = 0
        # django_tags_id_list = []
        # django_id_list=[]
        django_answer_list=[]
        django_qusetios_list=[]
        django_parent_id=[]
        django_question_title=[]
        django_question_body=[]
        count=0
        # with open(django_tags_filename, 'r', encoding='utf-8', errors="replace") as fin:
        #     reader = csv.reader(fin)
        #     header = None
        #     cnt = 0
        #     for row in reader:
        #         if cnt % 10000 is 0:
        #             print('has read data %s: %d/%d' % (collection_name, cnt, row_sum))
        #         cnt += 1
        #         if header is None:
        #             header = row
        #         else:
        #             obj = {}
        #             for i in range(0, len(header)):
        #                 obj[header[i]] =row[i]
        #             django_id_list.append(obj["Id"])
        #             django_tags_id_list.append(obj)
        #     fin.close()
        for item in list(db['django_questions'].find()):
            django_qusetios_list.append(item)
            django_parent_id.append(item["Id"])
            django_question_title.append(item["Title"])
            django_question_body.append(item["Body"])

        for item in list(db['django_answers'].find()):
            django_answer_list.append(item)

        # for obj in django_tags_id_list:
        #     if count % 1000is 0:
        #         print('has update data %s: %d/%d' % (collection_name, count, row_sum))
        #     count += 1
        #     # id=obj["Id"]
        #     # tag=obj["Tag"]
        #     Filter=obj[filter]
        #     Add_filed=obj[add_filed]
            # if count<5:
            # print(list(db[collection_name].find({filter_filed:Filter})))
            #找到对应的object增加字段，注意如果筛选条件对应多个object都要进行操作要加multi=True

        # for obj in django_answer_list:
        #     count+=1
        #     if count % 1000 is 0:
        #          print('has read data %s: %d' % (collection_name, count))
        #     db[collection_name].update({"Id":obj["Id"]},{"$set":{"Body":obj["Body"]}},multi=True)

        for obj in django_qusetios_list:
            count+=1
            if count % 1000 is 0:
                 print('has read data %s: %d' % (collection_name, count))
            Filter=obj[filter]
            Add_filed_title=obj["Title"]
            Add_filed_body=obj["Body"]
            db[collection_name].update({filter_filed:Filter},{"$set":{add_filed[1]:Add_filed_body}},multi=True)
            # print(list(db[collection_name].find({"ParentId":obj["Id"]})))
            # db[collection_name].update({filter_filed:Filter},{"$set":{add_filed[1]:Add_filed_body}},multi=True)

    def modify_filed_name(self,db,collection_name,old_filedname_list,new_filedname_list):
        for index in range(len(old_filedname_list)):
            db[collection_name].update({},{"$rename": {old_filedname_list[index]:new_filedname_list[index]}},multi=True)




if __name__ == '__main__':
    add_filed="Tag"
    filter_filed="ParentId"
    filter="Id"
    add_filed=["Title","QuestionBody"]
    django_tags=django_tags()
    db =django_tags.get_connection_mongodb(database_config)
    # django_tags.store_db_collection(db, tags_filename , 'django_tags')
    # django_tags.store_db_django_answers(db,'django_answers',"ParentId",answers_filename)
    # django_tags.append_tag_field_indb(db,'django_answers',add_filed,filter_filed,filter)
    # django_tags.store_db_django_answers(db,'django_questions',"Id",questions_filename)
    # django_tags.append_tag_field_indb(db,'django_answers_standard',add_filed,filter_filed,filter)
    # old_filedname_list=["Answer_Text","Answer_Link","Answer_Code","Answer_Id","Answewr_Body","Question_Title"]
    old_filedname_list=["AnswewrBody"]
    # new_filedname_list=["AnswerText","AnswerLink","AnswerCode","AnswerId","AnswerBody","QuestionTitle"]
    new_filedname_list=["AnswerBody"]
    django_tags.modify_filed_name(db,"django_answers_keyword_tfidf",old_filedname_list,new_filedname_list)