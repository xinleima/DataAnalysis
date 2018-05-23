import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAIN_DIR = os.path.join(ROOT_DIR, 'analysis_process')

DICTIONARY_FILENAME = os.path.join(MAIN_DIR, './output/tfidf_dictionary')
CORPUS_FILENAME = os.path.join(MAIN_DIR, './output/tfidf_corpus')
DOCS_FILENAME = os.path.join(MAIN_DIR, './output/tfidf_docs')
TFIDF_FILENAME = os.path.join(MAIN_DIR, './output/tfidf')
TOPIC_FILENAME = os.path.join(MAIN_DIR, './output/topic')

TOPIC_PARAMS_FILENAME = os.path.join(MAIN_DIR, './output/topic_params')
TOPIC_PARAMS_BODY_FILENAME = os.path.join(MAIN_DIR, './output/topic_params_body')
