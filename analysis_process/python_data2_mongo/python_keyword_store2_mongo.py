import csv
from pymongo import MongoClient
from utils.mongodb_utils import get_connection

def store_db_keyword_collection(db, filename, collection_name,key_word_list):
    db_collection = db[collection_name]
    row_sum = 0
    with open(filename, 'rb') as fin:
        row_sum = len(fin.readlines())
        fin.close()
    with open(filename, 'r', encoding='utf-8', errors="replace") as fin:
        reader = csv.reader(fin)
        header = None
        cnt = 0
        objs = []
        for row in reader:
            if cnt % 1000 is 0:
                print('insert into %s: %d/%d' % (collection_name, cnt, row_sum))
            if header is None:
                header = row
            else:
                obj = {}
                for i in range(0, len(header)):
                    obj[header[i]] = row[i]
                obj["KeyWord"]=key_word_list[cnt]
                cnt += 1
                # print(obj)
                objs.append(obj)
        db_collection.insert(objs)
        fin.close()


def change_db_keyword_collection(db,key_word_list):
    i=0
    for item in list(db['django_answers_keyword_tfidf'].find()):
        db['django_answers_keyword_tfidf'].update({'_id':item['_id']},{"$set":{"KeyWord" :key_word_list[i]}})
        # print(item["KeyWord"])
        i+=1

if __name__ == '__main__':
    db =get_connection()