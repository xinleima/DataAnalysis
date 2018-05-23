from gensim import models, similarities
from gensim.models import CoherenceModel, LdaMulticore

from data_process import preprocess
from data_standard import standard_data
from model import CorpusModel
from utils import constants, mongodb_utils, collections_utils


class TopicModel(object):
    def __init__(self, corpus_model: CorpusModel, num_topics=1000, iterations=50, passes=1, reload=False, reload_label=''):
        self.corpus_model = corpus_model
        self.num_topics = num_topics
        self.iterations = iterations
        self.passes = passes

        self.lda_model: models.ldamodel.LdaModel = None
        if reload:
            self.load(reload_label)
        else:
            self.build_model()
        self.similarity_model = similarities.MatrixSimilarity(self.lda_model[self.corpus_model.corpus])

    def get_score(self):
        coherence_model = CoherenceModel(model=self.lda_model,
                                         texts=self.corpus_model.documents,
                                         dictionary=self.corpus_model.dictionary,
                                         coherence='c_v')
        return coherence_model.get_coherence()

    def build_model(self):
        self.lda_model = LdaMulticore(
            corpus=self.corpus_model.corpus,
            id2word=self.corpus_model.dictionary,
            num_topics=self.num_topics,
            alpha=50 / self.num_topics,
            eta=0.1,
            iterations=self.iterations,
            passes=self.passes)

    def save(self, reload_label):
        self.lda_model.save(constants.TOPIC_FILENAME + '-' + reload_label)

    def load(self, reload_label):
        self.lda_model = models.ldamodel.LdaModel.load(constants.TOPIC_FILENAME + '-' + reload_label)

    def get_sim_docs(self, document, top=3):
        vec_bow = self.corpus_model.dictionary.doc2bow(document)
        vec_lda = self.lda_model[vec_bow]
        sims = self.similarity_model[vec_lda]
        sorted_sims = sorted(enumerate(sims), key=lambda item: -item[1])
        return sorted_sims[: top]

    def get_sim_tags(self, document, top=3):
        sim_docs = self.get_sim_docs(document, top)
        sim_doc_tags = []

        db = mongodb_utils.get_connection()

        for sim_doc in sim_docs:
            with db['python_standard_train'].find().skip(sim_doc[0]).limit(1) as doc_scan:
                for doc in doc_scan:
                    sim_doc_tags.append(doc['Tag'])

        return collections_utils.union_list(sim_doc_tags)


if __name__ == '__main__':
    def main():
        documents = [
            ['aa', 'bb', 'cc'],
            ['bb', 'dd', 'ee'],
            ['aa', 'ff', 'cc'],
            ['gg', 'ff', 'cw']
        ]
        corpus_model = CorpusModel(documents)
        model = TopicModel(corpus_model, num_topics=2)
        print(model.get_sim_tags(['aa', 'bb', 'cc']))

        # corpus_body_model = CorpusModel(reload=True, reload_label='body')
        # body_topic_model = TopicModel(corpus_body_model, iterations=500, num_topics=300)
        # print('body_TopicModel has created!')
        # text="<p>I've always liked doing it this way</p>\n\n<pre><code>result = {\n  'a': lambda x: x * 5,\n  'b': lambda x: x + 7,\n  'c': lambda x: x - 2\n}[value](x)\n</code></pre>\n\n<p><a href=\"http://blog.simonwillison.net/post/57956755106/switch\">From here</a></p>\n<p>I want to write a function in Python that returns different fixed values based on the value of an input index.  </p>\n\n<p>In other languages I would use a <code>switch</code> or <code>case</code> statement, but Python does not appear to have a <code>switch</code> statement.  What are the recommended Python solutions in this scenario?</p>\n"
        # codes, links, plain_text = standard_data(text)
        # print(body_topic_model.get_sim_tags(preprocess(plain_text)))

    main()
