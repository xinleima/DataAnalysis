import os
from data_process import DataProcess
from utils import constants
import utils.mongodb_utils


class ReverseIndexer(object):
    def __init__(self):
        db = utils.mongodb_utils.get_connection()
        self.words_count_collection = db['inverted_index_words_count']
        self.inverted_index_collection = db['inverted_index_collection']

    def count_words(self, document_words, doc_id):
        """词频统计."""
        result_dict = {}
        for word in document_words:
            if word not in result_dict:
                result_dict[word] = 1
            else:
                result_dict[word] += 1

        items = [{'word': key, 'count': value, 'doc_id': doc_id} for key, value in result_dict.items()]
        self.words_count_collection.insert(items)

    def sort_index(self):
        """对统计结果 <word, DocID, Freq> 排序."""
        word_counts_scan = self.words_count_collection.find()

        map_word_to_doc = {}

        for word_count in word_counts_scan:
            word = word_count['word']
            count = word_count['count']
            doc_id = word_count['doc_id']

            cur_document = None
            if word not in map_word_to_doc:
                map_word_to_doc[word] = {
                    'word': word,
                    'docs': [
                        {
                            'doc_id': doc_id,
                            'count': count
                        }
                    ],
                    'count': count
                }
            else:
                cur_document = map_word_to_doc[word]
                cur_document['count'] += count
                cur_document['docs'].append({
                    'doc_id': doc_id,
                    'count': count
                })

        words = map_word_to_doc.values()

        self.inverted_index_collection.insert(words)





if __name__ == '__main__':
    indexer = ReverseIndexer()

    db = utils.mongodb_utils.get_connection()
    db_collection = db["python_has_code"]
    data_process = DataProcess()
    words_list = data_process.textprocess('python_has_code')
    doc_id_list = data_process.get_doc_id('python_has_code')

    for i in range(len(words_list)):
        indexer.count_words(words_list[i], doc_id_list[i])

    indexer.sort_index()

    # 构建倒排索引
    # indexer.make_dictionnary()
