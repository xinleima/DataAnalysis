from data_process import parse_title, data_process
from model import CorpusModel, TopicModel, TfidfModel
from utils import mongodb_utils


def get_title_docs():
    db = mongodb_utils.get_connection()
    col = db['python_standard_train']

    title_docs = []
    with col.find() as items:
        for idx, item in enumerate(items):
            title = item['question_Title']
            _, _, title_doc = parse_title(title)
            title_docs.append(title_doc)
            if idx % 1000 == 0:
                print(idx)

    return title_docs


def get_body_docs():
    docs = data_process.textprocess('python_standard_train')
    return docs


def save_body_corpus_model():
    docs = get_body_docs()
    corpus_body_model = CorpusModel(docs)
    corpus_body_model.save('body')


def save_title_corpus_model():
    title_docs = get_title_docs()
    corpus_title_model = CorpusModel(title_docs)
    corpus_title_model.save('title')
    print('title_corpus_model has saved!')


def save_topic_model(corpus_body_model=None, corpus_title_model=None):
    if not corpus_body_model:
        corpus_body_model = CorpusModel(reload=True, reload_label='body')
    if not corpus_title_model:
        corpus_title_model = CorpusModel(reload=True, reload_label='title')

    title_topic_model = TopicModel(corpus_title_model, iterations=50, num_topics=150)
    print('title_TopicModel has created!')
    title_topic_model.save('title')
    print('title_topicModel has saved!')

    body_topic_model = TopicModel(corpus_body_model, iterations=500, num_topics=300)
    print('body_TopicModel has created!')
    body_topic_model.save('body')
    print('body_topicModel has saved!')


def save_model():
    corpus_body_model = CorpusModel(reload=True, reload_label='body')
    corpus_title_model = CorpusModel(reload=True, reload_label='title')

    tf_idf_model = TfidfModel(corpus_body_model)
    tf_idf_model.save('body')

    save_topic_model(corpus_body_model=corpus_body_model,
                     corpus_title_model=corpus_title_model)


if __name__ == '__main__':
    # save_model()
    # save_body_corpus_model()
    # save_title_corpus_model()
    save_topic_model()
