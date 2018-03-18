from pymongo import MongoClient
import string
import csv
import pickle
import re
import sys
import urllib.request
import nltk.stem
from index import database_config, get_connection_mongodb,answers_filename
import pickle
from gensim import corpora, models, similarities
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords


class reverse_index(object):
    def __init__(self):
        self.english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', '<', '>','=','/','--','{','}','< /']
        self.code_mode=['/code','code']



    # 将每个文档去除标点后，再进行词频统计
    def count_words(self, document, docID):
        result_dict = {}
        delset = string.punctuation

        line = str(document)
        line = line.translate(delset)  # 去除标点
        word_array = []
        words = line.split()
        for word in words:
            if word in result_dict:
                result_dict[word] += 1
            else:
                result_dict[word] = 1

        result_filename = './static/result.txt'

        file_out = open(result_filename, 'a')
        for key in result_dict.keys():
            str_row=key + '\t' + str(docID) + '\t' + str(result_dict[key]) + '\n'
            # str_content=str_row.encode("utf-8")
            # file_out.write(key + '\t' + str(docID) + '\t' + str(result_dict[key]) + '\n')
            file_out.write(str_row)
            print(str_row,'utf-8')
        file_out.close()
        print("ok!")

    def process_all_documents(self, collection_name):
        db = get_connection_mongodb(database_config)
        collection = db[collection_name]
        i=0
        for loop in collection.find({}):
            if i<1:
                body = loop["Body"].encode("utf-8")
                body=str(body,'utf-8')
                parent_id = loop["ParentId"].encode("utf-8")
                parent_id=str(parent_id,'utf-8')
                self.count_words(body, parent_id)
                i+=1




if __name__ == '__main__':
    indexer = reverse_index()
    # filename = 'static/input.txt'
    # file_in = open(filename, 'r')
    # indexer.process_all_documents('answers')

