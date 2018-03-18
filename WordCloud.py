import re
import sys
import urllib.request
import nltk.stem
from index import database_config, get_connection_mongodb,answers_filename,django_answers_filename,store_db_collection,django_answers_standard_filename
import pickle
from gensim import corpora, models, similarities
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import csv
from pymongo import MongoClient
from os import path
from scipy.misc import imread
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


d = path.dirname('.')

# file_object = open('django_answers_keyword_tfidf.txt','r',encoding='utf-8')
file_object = open('django_answers_keyword_tfidf_nonly.txt','r',encoding='utf-8')
text = file_object.read()


alice_coloring = imread("mermaid.jpg")


def get_connection_mongodb(config):
    connect = MongoClient(config['ip'], config['port'])
    return connect[config['dbName']]



def store_txt(db, collection_name):
    db_collection = db[collection_name]
    row_sum = 0
    key_word_list=[]
    # f = open("django_answers_keyword_tfidf.txt", "w",encoding='utf-8')
    f = open("django_answers_keyword_tfidf_nonly.txt", "w",encoding='utf-8')
    for item in list(db[collection_name].find()):
        key_word=item["KeyWord"]
        for word in key_word:
            key_word_list.append(word)
            f.write(word + "\n")
    f.close()

if __name__ == '__main__':
    db = get_connection_mongodb(database_config)
    # store_txt(db,"django_answers_keyword_tfidf_nonly")
    wc = WordCloud(background_color="white", #背景颜色
    max_words=2000,# 词云显示的最大词数
    mask=alice_coloring,#设置背景图片
    stopwords=STOPWORDS.add("said"),
    max_font_size=60, #字体最大值
    random_state=42)
    # 生成词云, 可以用generate输入全部文本(中文不好分词),也可以我们计算好词频后使用generate_from_frequencies函数
    wc.generate(text)
    # wc.generate_from_frequencies(txt_freq)
    # txt_freq例子为[('词a', 100),('词b', 90),('词c', 80)]
    # 从背景图片生成颜色值
    image_colors = ImageColorGenerator(alice_coloring)

    # 以下代码显示图片
    plt.imshow(wc)
    plt.axis("off")
    # 绘制词云
    plt.figure()
    # recolor wordcloud and show
    # we could also give color_func=image_colors directly in the constructor
    plt.imshow(wc.recolor(color_func=image_colors))
    plt.axis("off")
    # 绘制背景图片为颜色的图片
    plt.figure()
    plt.imshow(alice_coloring, cmap=plt.cm.gray)
    plt.axis("off")
    plt.show()
    # 保存图片
    wc.to_file("mermaid_wordcloud_nonly.jpg")

