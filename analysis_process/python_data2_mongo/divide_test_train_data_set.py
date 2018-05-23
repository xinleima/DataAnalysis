import random

from utils import mongodb_utils


def divide_test_train_data_set(test_rate=0.2):
    db = mongodb_utils.get_connection()
    col = db['python_standard_has_code']

    col_test = mongodb_utils.Collection(db['python_standard_test'])
    col_train = mongodb_utils.Collection(db['python_standard_train'])

    test_items_sum = 0
    train_items_sum = 0

    with col.find() as items:
        for item in items:
            rand_num = random.random()
            if rand_num < test_rate:
                test_items_sum += 1
                col_test.insert(item)
            else:
                train_items_sum += 1
                col_train.insert(item)

        col_test.insert_done()
        col_train.insert_done()

    print('test_rate: %f, real_test_rate: %f' % (test_rate, test_items_sum / (test_items_sum + train_items_sum)))


if __name__ == '__main__':
    divide_test_train_data_set()
