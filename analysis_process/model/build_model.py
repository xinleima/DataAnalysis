from data_process import data_process
from model import CorpusModel


def build_model():
    documents = data_process.textprocess('python_has_code')
    corpus_model = CorpusModel(documents)
    corpus_model.save()


if __name__ == '__main__':
    build_model()
