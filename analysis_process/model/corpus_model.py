import copy
from gensim import corpora
from gensim.models import CoherenceModel
from utils import constants, collections_utils, file_utils


class CorpusModel(object):
    def __init__(self, documents=None, reload=False, reload_label=''):
        if reload:
            self.load(reload_label)
        else:
            self.documents = documents
            self.dictionary = corpora.Dictionary(documents)
            self.corpus = [self.dictionary.doc2bow(doc) for doc in documents]

        self.map_id2word = collections_utils.reverse_key_value(self.dictionary.token2id)

    def update(self, documents):
        #更新词典
        dictionary = copy.deepcopy(self.dictionary)
        dictionary.add_documents(documents)
        #更新语料
        corpus2 = [dictionary.doc2bow(doc) for doc in documents]
        corpus = self.corpus + corpus2

        return dictionary, corpus

    def __save_docs(self, reload_label):
        #存储原始的word_list，二维数组
        #词语之间，分割，文档之间换行分割
        docs_str = '\n'.join([','.join(doc) for doc in self.documents])
        file_utils.write_string_to_file(constants.DOCS_FILENAME + '-' + reload_label, docs_str)

    def save(self, reload_label):
        #存储词典
        self.dictionary.save(constants.DICTIONARY_FILENAME + '-' + reload_label)
        #存储corpos
        corpora.MmCorpus.serialize(constants.CORPUS_FILENAME + '-' + reload_label, self.corpus)
        #存储document
        self.__save_docs(reload_label)

    def __load_docs(self, reload_label):
        # 加载原始的word_list，二维数组
        docs_str = file_utils.read_file_to_string(constants.DOCS_FILENAME + '-' + reload_label)
        doc_lines = docs_str.split('\n')
        self.documents = [doc_line.split(',') for doc_line in doc_lines]

    def load(self, reload_label):
        # 加载词典
        self.dictionary = corpora.Dictionary.load(constants.DICTIONARY_FILENAME + '-' + reload_label)
        # 加载corpos，因为是惰性地的，所以需要list一下
        self.corpus = list(corpora.MmCorpus(constants.CORPUS_FILENAME + '-' + reload_label))
        # 加载document
        self.__load_docs(reload_label)
