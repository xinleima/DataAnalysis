from pymongo import MongoClient
import string
import csv
import pickle
import re
import sys
import urllib.request
from index import database_config, questions_filename, answers_filename
import math
import time
from gensim import corpora, models, similarities

def test(filename):
    row_sum = 0
    codemode = re.compile(r'<pre><code>([\s\S]*?)</code></pre>')
    patternCode = re.compile(r'<p>|</p>|<a.*?>|</a>|<img.*?>')
    # with open(filename, 'rb') as fin:
    #     row_sum = len(fin.readlines())
    #     fin.close()
    with open(filename, 'r', encoding='utf-8', errors="replace") as fin:
        reader = csv.reader(fin)
        header = None
        cnt = 0
        objs = []
        for row in reader:
            cnt += 1
            if cnt < 6:
                print("====================================================")
                if header is None:
                    header = row
                else:
                    obj = {}
                    print(cnt)
                    for i in range(0, len(header)):
                        obj[header[i]] = patternCode.sub("", row[i])

                    # if 'Body' in obj:
                    body = obj['Body']
                    print('body:')
                    print(body)
                    print('--------------------------------------------------------')

                    has_code = codemode.findall(body)
                    if has_code:
                        print('code: ')
                        print(has_code)
            else:
                break
        fin.close()


if __name__ == '__main__':
    # test(answers_filename)
    corpus = [[(0, 1.0), (1, 1.0), (2, 1.0)],
      [(2, 1.0), (3, 1.0), (4, 1.0), (5, 1.0), (6, 1.0), (8, 1.0)],
      [(1, 1.0), (3, 1.0), (4, 1.0), (7, 1.0)],
          [(0, 1.0), (4, 2.0), (7, 1.0)],
          [(3, 1.0), (5, 1.0), (6, 1.0)],
         [(9, 1.0)],
        [(9, 1.0), (10, 1.0)],
          [(9, 1.0), (10, 1.0), (11, 1.0)],
         [(8, 1.0), (10, 1.0), (11, 1.0)]]

    tfidf = models.TfidfModel(corpus)
    vec=[[0,1],[1,4]]
    print(tfidf[vec])


