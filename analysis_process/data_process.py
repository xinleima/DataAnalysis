import pickle
import re
import sys
import urllib.request
import nltk.stem

from clean_code import pattern, bad_code_word, english_punctuations, bad_noun_word, commentmode, docmode,\
    import_library_mode, patternCode, codemode,filter_word,check_split_word,clean_code_label
from index import database_config, get_connection_mongodb,answers_filename,django_answers_filename,store_db_collection,django_answers_standard_filename,django_answers_keyword_tfidf_filename,python_answers_filename
import pickle
from gensim import corpora, models, similarities
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import regexp_tokenize
import csv
from pymongo import MongoClient
from get_python_lib import get_django_lib, get_standard_lib, print_array


class dataprocess:
    def get_connection_mongodb(self,config):
        connect = MongoClient(config['ip'], config['port'])
        return connect[config['dbName']]

    # #在数据中提取出代码部分以及链接到别的问题的代码
    # def process(self,db,filename, collection_name):
    #     db_collection = db[collection_name]
    #     row_sum = 0
    #     cnt = 0
    #     #匹配代码
    #     codemode = re.compile(r'<pre><code>([\s\S]*?)</code></pre>')
    #     #匹配链接
    #     linkmode=re.compile(r'<a href=\"([\s\S]*?)">')
    #     patternCode = re.compile(r'<p>|</p>|<a.*?>([\s\S]*?)</a>|<img.*?>')
    #     objs = []
    #     with open(filename, 'r', encoding='utf-8', errors="replace") as fin:
    #         reader = csv.reader(fin)
    #         header = None
    #
    #         for row in reader:
    #             if cnt >= 41010:
    #                 break
    #
    #             if cnt % 1000 is 0:
    #                 print('insert into %s: %d/%d' % (collection_name, cnt, row_sum))
    #             if header is None:
    #                 header = row
    #             else:
    #                 obj = {}
    #                 cnt += 1
    #                 for i in range(0, len(header)):
    #                     obj[header[i]] = row[i]
    #                 # if 'Body' in obj:
    #                 obj['Body'] = obj['Body'].replace("<blockquote>", "")
    #                 obj['Body'] = obj['Body'].replace("</blockquote>", "")
    #                 #找到代码部分，存放在list里面
    #                 has_code = codemode.findall(obj['Body'])
    #                 #找到链接部分，存放在list里面
    #                 has_link=linkmode.findall(obj['Body'])
    #                 #新增code字段
    #                 obj["answer_Code"]= has_code
    #                 #新增link字段
    #                 obj["answer_Link"]=has_link
    #                 #新增text字段，保存非代码的文本部分
    #                 obj["answer_Text"]= patternCode.sub("", obj["Body"])
    #                 #将body除去代码字段,得到文本字段
    #                 if has_code:
    #                     #文本部分除去代码
    #                     obj["answer_Text"]=codemode.sub("",obj["answer_Text"])
    #                 if has_link:
    #                     obj["answer_Text"]=linkmode.sub("",obj["answer_Text"])
    #                 #文本部分除去换行
    #                 obj["answer_Text"]= obj["answer_Text"].replace("\n","")
    #                 # print(cnt)
    #                 # print(obj["answer_Code"])
    #                 # print(obj["answer_Link"])
    #                 # print(obj["answer_Text"])
    #                 objs.append(obj)
    #     cnt = 0
    #     for obj in objs:
    #         db[collection_name].update({"answer_Id":obj["Id"]},{"$set":{"answer_Code": obj["answer_Code"],"answer_Link":obj["answer_Link"],"answer_Text":obj["answer_Text"]}})
    #         if cnt % 1000 is 0:
    #             print('insert into %s: %d' % (collection_name, cnt))
    #         cnt+=1
    #     fin.close()

    #分析文本片段
    def nltk_text(self,text):
        s = nltk.stem.SnowballStemmer('english')
        word_engStop = nltk.corpus.stopwords.words('english')
        texts_token=regexp_tokenize(text, pattern)
        for word in texts_token:
                    append_list=[]
                    tag=False
                    tag,append_list=check_split_word(word)
                    if(tag):
                        texts_token.remove(word)
                        texts_token= texts_token+append_list
        #词的字母全转成小写
        texts_tokenized = [word.lower() for word in texts_token]

        #只保留名词yg
        tagged = nltk.pos_tag(texts_tokenized)
        tagged_filter = filter(filter_word, tagged)
        tokens_filter = list(map(lambda item: item[0], tagged_filter))


        #用nltk的包除去英语停用词
        # texts_filtered_stopwords = [word for word in texts_tokenized if not word in word_engStop ]
        texts_filtered_stopwords = [word for word in tokens_filter if not word in word_engStop ]
        #词干化处理+除去英文标点
        texts_filtered = [s.stem(word) for word in texts_filtered_stopwords if not word in english_punctuations]
        #除去list中的无意义的代码关键字
        texts_filtered_nocode=[word for word in texts_filtered if not word in bad_code_word]
        #除去list中的无意义的名词
        texts_filtered_nobadnounword=[word for word in texts_filtered_nocode if not word in bad_noun_word]
        return texts_filtered_nobadnounword

    #分析代码片段
    def nltk_code(self,code_raw):
        code_all = []
        # 注释
        comment = []
        comment1 = []
        # 注释doc
        doc = []
        # 代码中标明引入的库
        import_libraries = []
        for code in code_raw:
            code=clean_code_label(code)
            print(code)
            comment.extend(commentmode.findall(code))
            doc.extend(docmode.findall(code))
            code = commentmode.sub("", code)
            code = docmode.sub("", code)
            import_libraries.extend(import_library_mode.findall(code))
            code = import_library_mode.sub("", code)
            code=code.replace("\n"," ")
            # 去除注释的代码
            code_all.append(code)

        code_token = []
        for code in code_all:
            code_token.append(regexp_tokenize(code,pattern))
        print("---comment---")
        print(comment)
        print("---lib---")
        print(import_libraries)
        print("---doc---")
        print(doc)
        print("---code---")
        print(code_token)
        return comment,import_libraries,doc,code_token




    def textprocess(self,collection_name):
        i=0
        db = get_connection_mongodb(database_config)
        words_list=[]
        comment_list=[]
        lib_list=[]
        doc_list=[]
        code_word_list=[]

        for item in list(db[collection_name].find()):
            if i<50:
                # if i % 1000 is 0:
                #     print('has deal with text %s: %d' % (collection_name, i))
                #除去问题内容里的链接
                item["question_Body"]=patternCode.sub("",item["question_Body"])
                #除去问题里的代码片段
                item["question_Body"]=codemode.sub("", item["question_Body"])
                # #除去问题文本里的换行
                item["question_Body"]= item["question_Body"].replace("\n"," ")
                #原始文本，一段文字，包括问题标题，除去代码片段的问题内容，除去代码片段的回答内容
                text=item["question_Body"]+"  "+item["answer_Text"]

                #分析代码片段
                print("第%d个" % i)

                comment,import_libraries,doc,code_token=self.nltk_code(item["answer_Code"])
                comment_list.append(comment)
                lib_list.append(import_libraries)
                doc_list.append(doc)
                code_word_list.append(code_token)
                print("--------------------------")

                #分析文本片段
                words_list.append(self.nltk_text(text))

                i+=1
            else:
                break

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
            print ("doc in corpus tfidf:=====>",doc)
            print(i)
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
                    print(new_dict[key_word0[0]],num0)
                if num1!=0:
                    key_word.append(new_dict[key_word1[0]])
                    print(new_dict[key_word1[0]],num1)
                if num2!=0:
                    key_word.append(new_dict[key_word2[0]])
                    print(new_dict[key_word2[0]],num2)
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
    # data_process.process(db,python_answers_filename,'python_answers_with_question')
    #
    words_list=data_process.textprocess('python_has_code')
    # dic=data_process.build_dictionary(words_list)
    # new_dict=data_process.reverse_dic(dic.token2id)
    # print("=====print new dic====")
    # print(new_dict)
    # corpus_tfidf,key_word_list=data_process.build_tfidfModel(words_list,new_dict)
    # corpus_lda=data_process.TopicModel(words_list,new_dict)

    # data_process.store_db_collection(db, questions_filename, 'questions_process')
    # data_process.store_db_collection(db,answers_filename, 'answers_process')
    # data_process.store_db_keyword_collection(db,django_answers_keyword_tfidf_filename,"django_answers_keyword_tfidf_nonly",key_word_list)
    # data_process.change_db_keyword_collection(db,key_word_list)

    # django_lib = get_django_lib()
    # print(len(django_lib))

    # standard_lib = get_standard_lib()
    # count = 0
    # for item in standard_lib:
    #     count += len(item[1])
    # print(count)

