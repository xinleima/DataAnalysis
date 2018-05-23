from model import CorpusModel, TopicModel, model_saver
from utils import file_utils, constants


def train_lad_model():
    # corpus_title_model = CorpusModel(reload=True, reload_label='title')
    corpus_body_model = CorpusModel(reload=True, reload_label='body')
    print('corpus_body_model has loaded!')

    iterations = 1000
    topics_num=300
    # for topics_num in range(200, 351, 50):
    title_topic_model = TopicModel(corpus_body_model,
                                   num_topics=topics_num,
                                   iterations=iterations)
    score = title_topic_model.get_score()
    print("topics_num: %d, iterations: %d, score: %.6f" % (topics_num, iterations, score))
    file_utils.append_string_to_file(
        constants.TOPIC_PARAMS_BODY_FILENAME, "[%d, %d, %.6f],\n" % (topics_num, iterations, score))


if __name__ == '__main__':
    train_lad_model()
