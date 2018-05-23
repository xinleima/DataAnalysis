from gensim import corpora, models, similarities

from data_process import data_process, preprocess
from model import CorpusModel
from utils import constants


class TfidfModel(object):
    def __init__(self, corpus_model: CorpusModel, reload=False, reload_label=''):
        self.corpus_model = corpus_model
        if reload:
            self.load(reload_label)
        else:
            self.tfidf = models.TfidfModel(corpus_model.corpus)

    def save(self, reload_label):
        self.tfidf.save(constants.TFIDF_FILENAME + '-' + reload_label)

    def load(self, reload_babel):
        self.tfidf = models.TfidfModel.load(constants.TFIDF_FILENAME + '-' + reload_babel)

    def get_key_words(self, input_document, top=3):
        input_corpus = [self.corpus_model.dictionary.doc2bow(input_document)]

        tfidf_doc_list = self.tfidf[input_corpus]
        last_tfidf_doc = tfidf_doc_list[0]

        sorted_doc = sorted(last_tfidf_doc, key=lambda item: item[1], reverse=True)
        key_words = [self.corpus_model.map_id2word[item[0]] for item in sorted_doc[: top]]

        return key_words


if __name__ == '__main__':
    def main():
        # documents = [
        #     ['aa', 'bb', 'cc'],
        #     ['bb', 'dd', 'ee'],
        #     ['aa', 'bb2', 'cc']
        # ]
        documents = data_process.textprocess('python_standard_has_code')

        corpus_model = CorpusModel(documents)
        corpus_model.save()

        tf_idf_model = TfidfModel(corpus_model)
        # tf_idf_model = TfidfModel(corpus_model,reload=True)
        tf_idf_model.save()

        new_text = "HTTP status code 503, \"Service Unavailable\", means that (for some reason) the server wasn't able to process your request. It's usually a transient error. I you want to know if you have been blocked, just try again in a little while and see what happens.</p>\n\n<p>It could also mean that you're fetching pages too quickly. The fix is not to do this by keeping concurrent requests at 1 (and possibly adding a delay). Be polite.</p>\n\n<p>And you <em>will</em> encounter various errors if you are scraping a enough. Just make sure that your crawler can handle them."
        document = preprocess(new_text)
        print(document)

        print(tf_idf_model.get_key_words(document))


    main()
