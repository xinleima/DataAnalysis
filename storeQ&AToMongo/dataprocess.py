import pickle
import re
import sys
import urllib.request
import nltk.stem
from index import database_config, get_connection_mongodb,answers_filename,django_answers_filename,store_db_collection,django_answers_standard_filename,django_answers_keyword_tfidf_filename
import pickle
from gensim import corpora, models, similarities
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import regexp_tokenize
import csv
from pymongo import MongoClient


def filter_word(item):
    # return (not item[1].startswith('V')) and (item[1] != 'IN') and (item[1] != '.') and (item[1] != 'RB')
    return item[1]=='NN'


class StemmedCountVectorizer(CountVectorizer):
    def build_analyzer(self):
        english_stemmer = nltk.stem.SnowballStemmer('english')
        analyzer = super(StemmedCountVectorizer, self).build_analyzer()
        return lambda doc: (english_stemmer.stem(w) for w in analyzer(doc))


class StemmedTfidfVectorizer(TfidfVectorizer):
    def build_analyzer(self):
        english_stemmer = nltk.stem.SnowballStemmer('english')
        analyzer = super(StemmedTfidfVectorizer, self).build_analyzer()
        return lambda doc: (english_stemmer.stem(w) for w in analyzer(doc))



class dataprocess:
    def __init__(self):
        self.english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', '<', '>','=','/','--','{','}','< /']
        self.bad_code_word=['/code', 'code', 'ul', '/ul', 'li', '/li', 'b', '/b', 'p', '/p', 'n\'t', "\'\'", "/pre", "pre", "\'", "``", "\'s", "\'m", 'use', '=']
        self.bad_noun_word=['data','it','item','example','id','user','name','max_length','text','false','default','us','dev','task','block','code','detail','comment','e.g','em','strong']
        self.codemode = re.compile(r'<pre><code>([\s\S]*?)</code></pre>')
        self.linkmode=re.compile(r'<a href=\"([\s\S]*?)">')
        self.patternCode = re.compile(r'<p>|</p>|<a.*?>([\s\S]*?)</a>|<img.*?>')
        # self.pattern = r"""(?x)     # 设置以编写较长的正则条件
        # |\w+(?:[\.]\w+)*       # 用.链接的词汇
        # |(?:[A-Z]\.)+          # 缩略词
        # |\$?\d+(?:\.\d+)?%?    # 货币、百分数
        # |\w+(?:[-']\w+)*       # 用连字符链接的词汇
        # |\.\.\.                # 省略符号
        # |(?:[.,;"'?():-_`])    # 特殊含义字符
        #
        # """
        self.pattern =r"""\w+(?:[\.]\w+)*|(?:[A-Z]\.)+|\$?\d+(?:\.\d+)?%?|\w+(?:[-']\w+)*|\.\.\|(?:[.,;"'?():-_`])"""

    def get_connection_mongodb(self,config):
        connect = MongoClient(config['ip'], config['port'])
        return connect[config['dbName']]


    #判断“.”两端的词是否需要拆分
    def check_split_word(self,str):
        codemode = re.compile(r'<（\S）*>([\s\S]*.)</（\S）*>')
        tag=False
        # print(text)
        if(str.find(".")):
            str_list=str.split(".")
        if(str_list[1]==str_list[1].capitalize( )):
            tag=True
            return tag,str_list
        else:
            return tag,str


        # for str in text:
        #     if (str.find("?")!=-1):
        #         tag=True
        #         str_list=str.split("?")
        #         text.extend(str_list)
        #
        #     if (str.find("(")!=-1):
        #         tag=True
        #         str_list=str.split("(")
        #         text.extend(str_list)
        #
        #     if (str.find(")")!=-1):
        #         tag=True
        #         str_list=str.split(")")
        #         text.extend(str_list)
        # # print(text)
        #     if tag:
        #         text.remove(str)
        #         tag=False
        return text







    #在数据中提取出代码部分以及链接到别的问题的代码
    def process(self,db,filename, collection_name):
        db_collection = db[collection_name]
        row_sum = 0
        #匹配代码
        codemode = re.compile(r'<pre><code>([\s\S]*?)</code></pre>')
        #匹配链接
        linkmode=re.compile(r'<a href=\"([\s\S]*?)">')
        patternCode = re.compile(r'<p>|</p>|<a.*?>([\s\S]*?)</a>|<img.*?>')
        with open(filename, 'r', encoding='utf-8', errors="replace") as fin:
           reader = csv.reader(fin)
           header = None
           cnt = 0
           objs = []
           for row in reader:
               if cnt % 1000 is 0:
                   print('insert into %s: %d/%d' % (collection_name, cnt, row_sum))
                   cnt += 1
               if header is None:
                   header = row
               else:
                   obj = {}
                   for i in range(0, len(header)):
                       obj[header[i]] = row[i]
                   # if 'Body' in obj:
                   body = obj['Body']
                   # print('body:')
                   # print(body)
                   # print('--------------------------------------------------------')
                    #找到代码部分，存放在list里面
                   has_code = codemode.findall(body)
                   #找到链接部分，存放在list里面
                   has_link=linkmode.findall(body)
                   #新增code字段
                   obj["Code"]= has_code
                   #新增link字段
                   obj["Link"]=has_link
                   #新增text字段，保存非代码的文本部分
                   obj["Text"]= patternCode.sub("", obj["Body"])
                   #将body除去代码字段,得到文本字段
                   if has_code:
                       #文本部分除去代码
                       obj["Text"]=codemode.sub("",obj["Text"])
                       #文本部分除去换行
                       obj["Text"]= obj["Text"].replace("\n","")
                       # print('code: ')
                       # print(has_code)
                       # print("text:")
                       # print(obj["Text"])
                       # print("link:")
                       # print(obj["Link"])
                   objs.append(obj)
        db_collection.insert(objs)
        fin.close()

    def textprocess(self,collection_name):
        i=0
        db = get_connection_mongodb(database_config)
        db_collection = db[collection_name]
        s = nltk.stem.SnowballStemmer('english')
        word_engStop = nltk.corpus.stopwords.words('english')
        words_list=[]
        for item in list(db[collection_name].find()):
            # if i<50:
            if i % 1000 is 0:
                print('has deal with text %s: %d' % (collection_name, i))
            #除去问题内容里的链接
            item["QuestionBody"]=self.patternCode.sub("",item["QuestionBody"])
            #除去问题里的代码片段
            item["QuestionBody"]=self.codemode.sub("", item["QuestionBody"])
            #除去问题文本里的换行
            item["QuestionBody"]= item["QuestionBody"].replace("\n","")
            #原始文本，一段文字，包括问题标题，除去代码片段的问题内容，除去代码片段的回答内容
            text=item["Title"]+"  "+item["QuestionBody"]+"  "+item["Text"]


            texts_token=regexp_tokenize(text,self.pattern)
            # print("----------before noun---------")
            # print(texts_token)

            # print( texts_token)
            #词的字母全转成小写
            texts_tokenized = [word.lower() for word in texts_token]

            #只保留名词yg
            tagged = nltk.pos_tag(texts_tokenized)
            tagged_filter = filter(filter_word, tagged)
            tokens_filter = list(map(lambda item: item[0], tagged_filter))


            #用nltk的包除去英语停用词
            # texts_filtered_stopwords = [word for word in texts_tokenized if not word in word_engStop ]
            texts_filtered_stopwords = [word for word in tokens_filter if not word in word_engStop ]
            #除去英文标点
            texts_filtered = [s.stem(word) for word in texts_filtered_stopwords if not word in self.english_punctuations]
            #除去list中的无意义的代码关键字
            texts_filtered_nocode=[word for word in texts_filtered if not word in self.bad_code_word]
            #除去list中的无意义的名词
            texts_filtered_nobadnounword=[word for word in texts_filtered_nocode if not word in self.bad_noun_word]
            words_list.append(texts_filtered_nobadnounword)
            # print(texts_filtered_nobadnounword)
            i+=1
            # else:
            #     break

        print("data total number")
        print(i)
        return words_list


    def reverse_dic(self,words_list):
        new_dict = {v:k for k,v in words_list.items()}
        return new_dict



    def build_dictionary(self, words_list):
        print ("==== build dictionary from tokenized text ... ====")
        self.dictionary = corpora.Dictionary(words_list)
        # print self.dictionary.token2id
        # print(self.dictionary.token2id)
        print ("====  dictionary complete ====")
        return self.dictionary

    def build_tfidfModel(self, words_list,new_dict):
        print ("==== build tfidfmodel for corpus from tokenized text ... ====")
        i=0
        key_word_list=[]
        corpus = [self.dictionary.doc2bow(word) for word in words_list]
        # print corpus
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        for doc in corpus_tfidf:
            if i % 1000 is 0:
                print('has deal with keyword : %d' % ( i))
            key_word=[]
            # if i<100:
            # print ("doc in corpus tfidf:=====>",doc)
            i+=1
            if doc:
                #根据tf-idf值的大小来确定每篇文章3个关键词
                num0=0
                key_word0=[]
                num1=0
                key_word1=[]
                num2=0
                key_word2=[]
                for item in doc:
                    if item[1]>num0:
                        key_word2=key_word1
                        key_word1=key_word0
                        key_word0=item
                        num2=num1
                        num1=num0
                        num0=item[1]
                    elif item[1]>num1:
                        key_word2=key_word1
                        key_word1=item
                        num2=num1
                        num1=item[1]
                    elif item[1]>num2:
                        key_word2=item
                        num2=item[1]

                if num0!=0:
                    key_word.append(new_dict[key_word0[0]])
                    # print(new_dict[key_word0[0]],num0)
                if num1!=0:
                    key_word.append(new_dict[key_word1[0]])
                    # print(new_dict[key_word1[0]],num1)
                if num2!=0:
                    key_word.append(new_dict[key_word2[0]])
                    # print(new_dict[key_word2[0]],num2)
                key_word_list.append(key_word)
        # else:
        #     break
        print("==== tfidf model complete ====")
        return corpus_tfidf,key_word_list

    def TopicModel(self,words_list,new_dict):
        topic_templete=re.compile(r'(\d+)(\*)(\S+)(\+)(\d+)(\*)(\S+)(\+)(\d+)\*(\S+)')
        #得到document-term matrix
        corpus = [self.dictionary.doc2bow(word) for word in words_list]
        #运用lda模型
        lda = models.ldamodel.LdaModel(corpus=corpus,id2word=new_dict,num_topics=20,alpha='auto')
        # 至此得到的corpus_lda就是每个text的LDA向量，稀疏的，元素值是隶属与对应序数类的权重
        corpus_lda = lda[corpus]
        print(lda.print_topics(num_topics=200, num_words=3))
        for doc in corpus_lda:
            print ("doc similarity with each topic:===> ","\n", doc)
            for item in doc:
                print("the topic model is %s" %(item[0]))
                print("the similarity is %s" %(item[1]))
                topic=lda.show_topics(num_topics=200, num_words=3)[item[0]]
                print(topic)
        return corpus_lda



    def store_db_keyword_collection(self,db, filename, collection_name,key_word_list):
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


    def change_db_keyword_collection(self,db,key_word_list):
        i=0
        for item in list(db['django_answers_keyword_tfidf'].find()):
            db['django_answers_keyword_tfidf'].update({'_id':item['_id']},{"$set":{"KeyWord" :key_word_list[i]}})
            # print(item["KeyWord"])
            i+=1






if __name__ == '__main__':
    data_process=dataprocess()
    db =data_process.get_connection_mongodb(database_config)
    # data_process.process(db,django_answers_filename,'django_answers_standard')

    words_list=data_process.textprocess('django_answers_standard')
    dic=data_process.build_dictionary(words_list)
    new_dict=data_process.reverse_dic(dic.token2id)
    print("=====print new dic====")
    print(new_dict)
    corpus_tfidf,key_word_list=data_process.build_tfidfModel(words_list,new_dict)
    # corpus_lda=data_process.TopicModel(words_list,new_dict)

    # data_process.store_db_collection(db, questions_filename, 'questions_process')
    # data_process.store_db_collection(db,answers_filename, 'answers_process')
    data_process.store_db_keyword_collection(db,django_answers_keyword_tfidf_filename,"django_answers_keyword_tfidf_nonly",key_word_list)
    # data_process.change_db_keyword_collection(db,key_word_list)