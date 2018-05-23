import os

from utils import constants


def read_file_to_string(filename):
    abs_filename = os.path.join(constants.ROOT_DIR, filename)
    with open(abs_filename, 'r', encoding='UTF-8') as fin:
        text = fin.read()
    return text


def write_string_to_file(filename, string):
    abs_filename = os.path.join(constants.ROOT_DIR, filename)
    with open(abs_filename, 'w', encoding='UTF-8') as fout:
        fout.write(string)


def append_string_to_file(filename, string):
    abs_filename = os.path.join(constants.ROOT_DIR, filename)
    with open(abs_filename, 'a', encoding='UTF-8') as fout:
        fout.write(string)


if __name__ == '__main__':
    append_string_to_file(constants.TOPIC_PARAMS_FILENAME, 'test')
