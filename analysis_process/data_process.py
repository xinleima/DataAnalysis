import pickle
import re
import sys
import urllib.request
import nltk.stem

from bs4 import BeautifulSoup
from clean_code import pattern, bad_code_word, english_punctuations, bad_noun_word, commentmode, docmode, \
    import_library_mode, patternCode, codemode, filter_word, check_split_word, clean_code_label, code_lan, \
    python_artifactor, filter_word_4title
from index import database_config, get_connection_mongodb, answers_filename, django_answers_filename, \
    store_db_collection, django_answers_standard_filename, django_answers_keyword_tfidf_filename, \
    python_answers_filename
import pickle
from gensim import corpora, models, similarities
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import regexp_tokenize
import csv
from pymongo import MongoClient
from get_python_lib import get_django_lib, get_standard_lib, print_array
import parse_code
import get_python_lib
from nltk.stem import WordNetLemmatizer

from utils import collections_utils
from utils.mongodb_utils import get_connection
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer


def text_simple_process(text):
    soup = BeautifulSoup(text, 'lxml')
    text = soup.get_text(' ')
    text = text.replace("\n", " ")
    texts_token = regexp_tokenize(text, pattern)
    for word in texts_token:
        append_list = []
        tag = False
        tag, append_list = check_split_word(word)
        if (tag):
            texts_token.remove(word)
            texts_token = texts_token + append_list
    # 词的字母全转成小写
    texts_tokenized = [word.lower() for word in texts_token]
    texts_filtered = [word for word in texts_tokenized if
                      not word in english_punctuations]
    word_list = lemmatize_word_list(texts_filtered)
    return word_list




def get_plain_text(text):
    soup = BeautifulSoup(text, 'lxml')
    for tag in soup.select('pre code, a'):
        tag.extract()
    plain_text = soup.get_text(' ')
    return plain_text

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    if treebank_tag.startswith('V'):
        return wordnet.VERB
    if treebank_tag.startswith('N'):
        return wordnet.NOUN
    if treebank_tag.startswith('R'):
        return wordnet.ADV
    return wordnet.NOUN


def lemmatize_word_list(word_list):
    lemmatizer = WordNetLemmatizer()
    lemmatizered_word_list = [lemmatizer.lemmatize(word, pos=get_wordnet_pos(pos)) for word, pos in pos_tag(word_list)]
    return lemmatizered_word_list

def preprocess(text):
    soup = BeautifulSoup(text, 'lxml')
    text = soup.get_text(' ')
    text = text.replace("\n", " ")
    word_eng_stop = nltk.corpus.stopwords.words('english')
    texts_token = regexp_tokenize(text, pattern)
    for word in texts_token:
        append_list = []
        tag = False
        tag, append_list = check_split_word(word)
        if (tag):
            texts_token.remove(word)
            texts_token = texts_token + append_list
    # 词的字母全转成小写
    texts_tokenized = [word.lower() for word in texts_token]

    # 只保留名词yg
    tagged = nltk.pos_tag(texts_tokenized)
    tagged_filter = filter(filter_word, tagged)
    tokens_filter = list(map(lambda item: item[0], tagged_filter))

    # 用nltk的包除去英语停用词
    # texts_filtered_stopwords = [word for word in texts_tokenized if not word in word_eng_stop ]
    texts_filtered_stopwords = [word for word in tokens_filter if not word in word_eng_stop]
    # 词性还原
    lemmatizer = WordNetLemmatizer()
    # 词性还原+除去英文标点
    texts_filtered = [lemmatizer.lemmatize(word, pos=wordnet.NOUN) for word in texts_filtered_stopwords if
                      not word in english_punctuations]
    # # 除去list中的无意义的代码关键字
    # texts_filtered_nocode = [word for word in texts_filtered if not word in bad_code_word]
    # 除去list中的无意义的名词
    texts_filtered_nobadnounword = [word for word in texts_filtered if not word in bad_noun_word]
    return texts_filtered_nobadnounword


def parse_title(title):
    word_engStop = nltk.corpus.stopwords.words('english')
    title_token = regexp_tokenize(title, pattern)
    # 词的字母全转成小写
    title_tokenized = [word.lower() for word in title_token]

    title_tokenized=lemmatize_word_list(title_tokenized)

    #词性标注
    tagged = nltk.pos_tag(title_tokenized)

    #过滤动词和数词
    #过滤器
    tagged_filter = filter(filter_word_4title, tagged)
    title_filter = list(map(lambda item: item[0], tagged_filter))

    #去除list中重复的词语
    title_filter = collections_utils.depulicate(title_filter)

    # 用nltk的包除去英语停用词
    title_filtered_stopwords = [word for word in title_filter if word not in word_engStop]

    language = list(set(title_tokenized).intersection(set(code_lan)))
    architure = list(set(title_tokenized).intersection(set(python_artifactor)))

    return language, architure, title_filtered_stopwords


class DataProcess:
    def get_connection_mongodb(self, config):
        connect = MongoClient(config['ip'], config['port'])
        return connect[config['dbName']]

    # 分析文本片段
    def nltk_text(self, text):
        soup = BeautifulSoup(text, 'lxml')
        text = soup.get_text(' ')
        text = text.replace("\n", " ")
        s = nltk.stem.SnowballStemmer('english')
        word_engStop = nltk.corpus.stopwords.words('english')
        texts_token = regexp_tokenize(text, pattern)
        for word in texts_token:
            append_list = []
            tag = False
            tag, append_list = check_split_word(word)
            if (tag):
                texts_token.remove(word)
                texts_token = texts_token + append_list
        # 词的字母全转成小写
        texts_tokenized = [word.lower() for word in texts_token]

        # 只保留名词yg
        tagged = nltk.pos_tag(texts_tokenized)
        tagged_filter = filter(filter_word, tagged)
        tokens_filter = list(map(lambda item: item[0], tagged_filter))

        # 用nltk的包除去英语停用词
        # texts_filtered_stopwords = [word for word in texts_tokenized if not word in word_engStop ]
        texts_filtered_stopwords = [word for word in tokens_filter if not word in word_engStop]
        # 词性还原
        lemmatizer = WordNetLemmatizer()
        # 词性还原+除去英文标点
        texts_filtered = [lemmatizer.lemmatize(word, pos=wordnet.NOUN) for word in texts_filtered_stopwords if
                          not word in english_punctuations]
        # 除去list中的无意义的代码关键字
        texts_filtered_nocode = [word for word in texts_filtered if not word in bad_code_word]
        # 除去list中的无意义的名词
        texts_filtered_nobadnounword = [word for word in texts_filtered_nocode if not word in bad_noun_word]
        return texts_filtered_nobadnounword

    # 分析代码片段
    def nltk_code(self, codes, has_django=False):
        """输入代码列表, 进行分析.

        :param codes: list(str). 一篇文章出现的代码片段集合.
        :return:
        """
        code_processed = []
        # 注释
        comment = []
        # 注释doc
        comment_doc = []
        # 代码中标明引入的库
        import_libraries = []
        package_find = []
        for code in codes:
            code = clean_code_label(code)

            comment.extend(commentmode.findall(code))
            comment_doc.extend(docmode.findall(code))
            code = commentmode.sub("", code)
            code = docmode.sub("", code)

            for import_item in import_library_mode.findall(code):
                if import_item[0] and import_item[1]:
                    import_models = import_item[1].replace(' ', '').split(',')
                    abs_import_models = ["%s.%s" % (import_item[0], import_model)
                                         for import_model in import_models]
                    import_libraries.extend(abs_import_models)
                elif import_item[2]:
                    import_libraries.extend(import_item[2].replace(' ', '').split(','))

            code = import_library_mode.sub("", code)
            code = code.replace("\n", " ")
            # 去除注释的代码
            code_processed.append(code)

        code_token = []
        for code in code_processed:
            package_find += parse_code.get_code_import_packages(code, has_django)
            code_token.append(regexp_tokenize(code, pattern))

        package_find = collections_utils.depulicate(package_find)


        # print("---comment---")
        # print(comment)
        # print("---lib---")
        # print(import_libraries)
        # print("---doc---")
        # print(doc)
        # print("---code---")
        # print(code_token)
        # print("---pakcage_find---")
        # print(pakcage_find)
        return comment, comment_doc, code_token, import_libraries, package_find

    def parse_title(self, title):
        word_engStop = nltk.corpus.stopwords.words('english')
        title_token = regexp_tokenize(title, pattern)
        # 词的字母全转成小写
        title_tokenized = [word.lower() for word in title_token]

        tagged = nltk.pos_tag(title_tokenized)
        tagged_filter = filter(filter_word_4title, tagged)


        title_filter = list(map(lambda item: item[0], tagged_filter))
        title_filter = collections_utils.depulicate(title_filter)

        # 用nltk的包除去英语停用词
        title_filtered_stopwords = [word for word in title_filter if word not in word_engStop]

        language = list(set(title_tokenized).intersection(set(code_lan)))
        architure = list(set(title_tokenized).intersection(set(python_artifactor)))

        # print("---language-----")
        # print(language)
        # print("---artifactor-----")
        # print(architure)
        # print("---title_tokenized-----")
        # print(title_filtered_stopwords)
        return language, architure, title_filtered_stopwords

    def textprocess(self, collection_name):
        db = get_connection_mongodb(database_config)
        body_docs = []

        with db[collection_name].find() as items:
            for idx, item in enumerate(items):
                # if idx % 1000 is 0:
                #     print('has deal with text %s: %d' % (collection_name, idx))
                if idx >100:
                    break
                else:
                    answer_plain_text = get_plain_text(item["answer_Text"])
                    question_plain_text = get_plain_text(item["question_Body"])

                    plain_text = question_plain_text + ' ' + answer_plain_text

                    body_docs.append(self.nltk_text(plain_text))

        return body_docs

    def reverse_dic(self, words_list):
        new_dict = {v: k for k, v in words_list.items()}
        return new_dict

    def get_doc_id(self, collection):
        conn = get_connection()
        collection = conn['python_has_code']
        doc_id_list = []
        doc_list = collection.find()
        for doc in doc_list:
            doc_id_list.append(doc["_id"])
        return doc_id_list

    def build_dictionary(self, words_list):
        # print("==== build dictionary from tokenized text ... ====")
        self.dictionary = corpora.Dictionary(words_list)
        # print self.dictionary.token2id
        # print(self.dictionary.token2id)
        # print("====  dictionary complete ====")
        return self.dictionary

    def build_tfidf_model(self, words_list, new_dict):
        corpus = [self.dictionary.doc2bow(word) for word in words_list]
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        for doc in corpus_tfidf:
            key_word = []
            if doc:
                print(doc)
                # 根据tf-idf值的大小来确定每篇文章3个关键词
                num0 = 0
                key_word0 = []
                num1 = 0
                key_word1 = []
                num2 = 0
                key_word2 = []
                for item in doc:
                    if item[1] > num0:
                        key_word2 = key_word1
                        key_word1 = key_word0
                        key_word0 = item
                        num2 = num1
                        num1 = num0
                        num0 = item[1]
                    elif item[1] > num1:
                        key_word2 = key_word1
                        key_word1 = item
                        num2 = num1
                        num1 = item[1]
                    elif item[1] > num2:
                        key_word2 = item
                        num2 = item[1]
                if num0 != 0:
                    key_word.append(new_dict[key_word0[0]])
                if num1 != 0:
                    key_word.append(new_dict[key_word1[0]])
                if num2 != 0:
                    key_word.append(new_dict[key_word2[0]])

        return corpus_tfidf, key_word

    def build_tfidfModel(self, words_list, new_dict):
        print("==== build tfidfmodel for corpus from tokenized text ... ====")
        i = 0
        key_word_list = []
        corpus = [self.dictionary.doc2bow(word) for word in words_list]
        print(corpus)
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        print(corpus_tfidf[len(corpus_tfidf) - 1])
        for doc in corpus_tfidf:
            if i % 1000 is 0:
                print('has deal with keyword : %d' % (i))
            key_word = []
            print("doc in corpus tfidf:=====>", doc)
            print(i)
            i += 1
            if doc:
                # 根据tf-idf值的大小来确定每篇文章3个关键词
                num0 = 0
                key_word0 = []
                num1 = 0
                key_word1 = []
                num2 = 0
                key_word2 = []
                for item in doc:
                    if item[1] > num0:
                        key_word2 = key_word1
                        key_word1 = key_word0
                        key_word0 = item
                        num2 = num1
                        num1 = num0
                        num0 = item[1]
                    elif item[1] > num1:
                        key_word2 = key_word1
                        key_word1 = item
                        num2 = num1
                        num1 = item[1]
                    elif item[1] > num2:
                        key_word2 = item
                        num2 = item[1]

                if num0 != 0:
                    key_word.append(new_dict[key_word0[0]])
                    print(new_dict[key_word0[0]], num0)
                if num1 != 0:
                    key_word.append(new_dict[key_word1[0]])
                    print(new_dict[key_word1[0]], num1)
                if num2 != 0:
                    key_word.append(new_dict[key_word2[0]])
                    print(new_dict[key_word2[0]], num2)
                key_word_list.append(key_word)
        print("==== tfidf model complete ====")
        return corpus_tfidf, key_word_list

    def TopicModel(self, words_list, new_dict):
        topic_templete = re.compile(r'(\d+)(\*)(\S+)(\+)(\d+)(\*)(\S+)(\+)(\d+)\*(\S+)')
        # 得到document-term matrix
        corpus = [self.dictionary.doc2bow(word) for word in words_list]
        # 运用lda模型
        lda = models.ldamodel.LdaModel(corpus=corpus, id2word=new_dict, num_topics=3, alpha='auto')
        # 至此得到的corpus_lda就是每个text的LDA向量，稀疏的，元素值是隶属与对应序数类的权重
        corpus_lda = lda[corpus]
        # print(lda.print_topics(num_topics=200, num_words=3))
        for doc in corpus_lda:
            print("doc similarity with each topic:===> ", "\n", doc)
            for item in doc:
                print("------------------------------------------")
                print(item)
                print("the topic model is %s" % (item[0]))
                print("the similarity is %s" % (item[1]))
                topic = lda.show_topics(num_topics=3, num_words=3)[item[0]]
                print(topic)
        return corpus_lda


data_process = DataProcess()

if __name__ == '__main__':
    def main():
        # text = """If it supports mod_python (which I guess it's what you mean), then sure, you can install it using the steps listed here: <a href=\"https://docs.djangoproject.com/en/1.1/howto/deployment/modpython/\" rel=\"nofollow\">ModPython docs</a></p>\n"""
        # plain_text=get_plain_text(text)

        # data_process = DataProcess()
        # db = data_process.get_connection_mongodb(database_config)
        # # data_process.process(db,python_answers_filename,'python_answers_with_question')
        # #
        words_list = data_process.textprocess('python_has_code')
        dic = data_process.build_dictionary(words_list)
        new_dict=data_process.reverse_dic(dic.token2id)
        print("=====print new dic====")
        print(new_dict)
        # corpus_tfidf,key_word_list=data_process.build_tfidfModel(words_list,new_dict)
        corpus_lda=data_process.TopicModel(words_list,new_dict)

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


    main()
