from data_process import data_process, preprocess, parse_title
from data_standard import standard_data
from model import CorpusModel, TfidfModel, TopicModel
from utils import collections_utils


class TagsGenerator(object):
    def __init__(self):
        self.title_corpus_model = CorpusModel(reload=True, reload_label='title')
        self.body_corpus_model = CorpusModel(reload=True, reload_label='body')
        print('corpus_model has loaded!')

        self.tfidf_model = TfidfModel(self.body_corpus_model, reload=True, reload_label='body')
        print('tfidf_model has loaded!')

        self.title_topic_model = TopicModel(self.title_corpus_model, reload=True, reload_label='title')
        print('topic_model_title has loaded!')
        self.body_topic_model = TopicModel(self.body_corpus_model, reload=True, reload_label='body')
        print('topic_model_body has loaded!')

    def gen_tags(self, input_title, input_body):
        codes, links, plain_text = standard_data(input_body)
        language, architure, title_filter = data_process.parse_title(input_title)

        title_tags = list(set(language) | set(architure) | set(title_filter))

        tfidf_tags = self.gen_tfidf_tags(plain_text)

        code_import_tags, code_find_tags = self.gen_code_tags(codes, 'django' in architure)

        title_topic_model_tags = self.gen_title_topic_model_tags(title_filter)
        body_topic_model_tags = self.gen_body_topic_model_tags(plain_text)

        intersection_tags = collections_utils.intersect_list([title_tags,
                                                              tfidf_tags,
                                                              code_import_tags,
                                                              code_find_tags,
                                                              title_topic_model_tags,
                                                              body_topic_model_tags])

        return collections_utils.remove_empty(intersection_tags), \
               collections_utils.remove_empty(title_tags), \
               collections_utils.remove_empty(tfidf_tags), \
               collections_utils.remove_empty(code_import_tags), \
               collections_utils.remove_empty(code_find_tags), \
               title_topic_model_tags, \
               body_topic_model_tags

    def gen_tfidf_tags(self, plain_text):
        doc_words = data_process.nltk_text(plain_text)
        # print(doc_words)
        key_words_tfidf = self.tfidf_model.get_key_words(doc_words)
        return key_words_tfidf

    def gen_code_tags(self, codes, has_django):
        comment, comment_doc, code_token, import_libraries, package_find = data_process.nltk_code(codes, has_django)
        return import_libraries, package_find

    def gen_body_topic_model_tags(self, plain_text):
        doc_word_list = preprocess(plain_text)
        return self.body_topic_model.get_sim_tags(doc_word_list)

    def gen_title_topic_model_tags(self, title_word_list):
        return self.body_topic_model.get_sim_tags(title_word_list)


if __name__ == '__main__':
    def main():
        tags_generator = TagsGenerator()

        print('input title:')
        title = input()
        print('input answer_body:')
        answer_body = input()

        while title != 'exit' and answer_body != 'exit':
            tags_generator.gen_tags(title, answer_body)

            print('input title:')
            title = input()
            print('input answer_body:')
            answer_body = input()

        # answer_body = """<p>I'm trying to add a new entry by using the admmin panel in Django. The problem is that I've already populated my DB with 200 records and if I try to add a new entry from admin I get a duplicated key error msg that keep increasing whenever I try the process again error:</p> <pre><code>duplicate key value violates unique constraint \"app_entry_pkey\" </code></pre> <p>admin.py:</p> <pre><code>admin.site.register(Entry) </code></pre> <p>model:</p> <pre><code>class Entry(models.Model): title = models.CharField(max_length=255)   url = models.TextField(max_length=255)    img = models.CharField(max_length=255)   def __unicode__(self):       return self.title </code></pre>"""
        # title = "Django add new entry from admin panel"


    main()
