import csv

from pymongo import MongoClient

database_config = {
    'ip': 'localhost',
    'port': 27017,
    'dbName': 'stackoverflow'
}

tags_filename = './static/Tags.csv'
questions_filename = './static/Questions.csv'
answers_filename = './static/Answers.csv'
django_tags_filename='./static/django_tags.csv'
django_answers_filename='./static/django_answers.csv'
django_answers_standard_filename='./static/django_answers_standard.csv'
django_answers_keyword_tfidf_filename='./static/django_answers_keyword_tfidf.csv'



def get_connection_mongodb(config):
    connect = MongoClient(config['ip'], config['port'])
    return connect[config['dbName']]


def store_db_collection(db, filename, collection_name):
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
            if cnt % 10000 is 0:
                print('insert into %s: %d/%d' % (collection_name, cnt, row_sum))
            cnt += 1
            if header is None:
                header = row
            else:
                obj = {}
                for i in range(0, len(header)):
                    obj[header[i]] = row[i]
                objs.append(obj)
        db_collection.insert(objs)
        fin.close()


if __name__ == '__main__':
    db = get_connection_mongodb(database_config)
    store_db_collection(db, questions_filename, 'questions')
    store_db_collection(db, answers_filename, 'answers')
