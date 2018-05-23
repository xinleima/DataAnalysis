from data_process import parse_title, data_process, get_plain_text, text_simple_process
from gen_tags import TagsGenerator
from utils import mongodb_utils, collections_utils


def tagen_test_data_set():
    tags_generator = TagsGenerator()

    db = mongodb_utils.get_connection()
    col = db['python_standard_test']

    col_operation = mongodb_utils.Collection(col)

    with col.find(no_cursor_timeout=True) as items:
        for idx, item in enumerate(items):
            if 'predicted_tags' in item:
                continue
            question_title = item['question_Title']
            question_body = item['question_Body']
            answer_body = item['answer_Body']
            body = question_body + '\n' + answer_body

            intersection_tags, title_tags, tfidf_tags, code_import_tags, code_find_tags, title_topic_model_tags, body_topic_model_tags = tags_generator.gen_tags(
                question_title, body)

            all_tags = intersection_tags + title_tags + tfidf_tags + code_import_tags + code_find_tags + title_topic_model_tags + body_topic_model_tags
            all_tags = collections_utils.depulicate(all_tags)

            col_operation.update(item['_id'], {
                'predicted_tags': {
                    'intersection': intersection_tags,
                    'title': title_tags,
                    'tfidf': tfidf_tags,
                    'code_import': code_import_tags,
                    'code_find': code_find_tags,
                    'body_topic_model_tags': body_topic_model_tags,
                    'title_topic_model_tags': title_topic_model_tags,
                    'all': all_tags
                }
            })

            if idx % 1000 == 0:
                print(idx)


def modify_title_tag():
    db = mongodb_utils.get_connection()
    col = db['python_standard_test']

    with col.find(no_cursor_timeout=True) as items:
        for idx, item in enumerate(items):
            question_title = item['question_Title']
            _, _, title_tags = parse_title(question_title)
            # db['django_answers_keyword_tfidf'].update({'_id': item['_id']},
            #                                           {"$set": {"predicted_tags.$.title": title_tags}})
            predicted_tags = item['predicted_tags']
            predicted_tags['code_find'] = collections_utils.depulicate(predicted_tags['code_find'])
            predicted_tags['title'] = title_tags
            col.update({'_id': item['_id']},
                       {'$set': {'predicted_tags': predicted_tags}})

            if idx % 1000 == 0:
                print(idx)


def modify_code_find():
    db = mongodb_utils.get_connection()
    col = db['python_standard_test']

    with col.find(no_cursor_timeout=True) as items:
        for idx, item in enumerate(items):
            answer_code = item["answer_Code"]
            predicted_tags = item['predicted_tags']
            title_tags = predicted_tags["title"]
            tfidf_tags = predicted_tags["tfidf"]
            code_import_tags = predicted_tags["code_import"]
            title_topic_model_tags = predicted_tags["title_topic_model_tags"]
            body_topic_model_tags = predicted_tags["body_topic_model_tags"]
            code_find_tags = predicted_tags['code_find']
            _, _, _, _, predicted_tags['code_find'] = data_process.nltk_code(answer_code)
            predicted_tags['all'] = collections_utils.depulicate(predicted_tags['all'])
            predicted_tags['intersection'] = collections_utils.intersect_list([title_tags,
                                                                               tfidf_tags,
                                                                               code_import_tags,
                                                                               code_find_tags,
                                                                               title_topic_model_tags,
                                                                               body_topic_model_tags])
            col.update({'_id': item['_id']},
                       {'$set': {'predicted_tags': predicted_tags}})

            if idx % 1000 == 0:
                print(idx)


def update_all_tags():
    db = mongodb_utils.get_connection()
    col = db['python_standard_test']

    with col.find(no_cursor_timeout=True) as items:
        for idx, item in enumerate(items):
            predicted_tags = item['predicted_tags']

            title_tags = predicted_tags["title"]
            tfidf_tags = predicted_tags["tfidf"]
            code_import_tags = predicted_tags["code_import"]
            title_topic_model_tags = predicted_tags["title_topic_model_tags"]
            body_topic_model_tags = predicted_tags["body_topic_model_tags"]
            code_find_tags = predicted_tags['code_find']

            predicted_tags['all'] = collections_utils.depulicate(title_tags + \
                                                                 tfidf_tags + \
                                                                 code_import_tags + \
                                                                 code_find_tags + \
                                                                 title_topic_model_tags + \
                                                                 body_topic_model_tags)
            predicted_tags['intersection'] = collections_utils.intersect_list([title_tags,
                                                                               tfidf_tags,
                                                                               code_import_tags,
                                                                               code_find_tags,
                                                                               title_topic_model_tags,
                                                                               body_topic_model_tags])
            col.update({'_id': item['_id']},
                       {'$set': {'predicted_tags': predicted_tags}})

            if idx % 1000 == 0:
                print(idx)


def remove_empty_items():
    db = mongodb_utils.get_connection()
    col = db['python_standard_test']

    with col.find(no_cursor_timeout=True) as items:
        for idx, item in enumerate(items):
            predicted_tags = item['predicted_tags']

            title_tags = predicted_tags["title"]
            tfidf_tags = predicted_tags["tfidf"]
            code_import_tags = predicted_tags["code_import"]
            title_topic_model_tags = predicted_tags["title_topic_model_tags"]
            body_topic_model_tags = predicted_tags["body_topic_model_tags"]
            code_find_tags = predicted_tags['code_find']

            code_find_tags = [item for item in code_find_tags if item]

            predicted_tags['code_find'] = code_find_tags
            predicted_tags['all'] = collections_utils.depulicate(title_tags + \
                                                                 tfidf_tags + \
                                                                 code_import_tags + \
                                                                 code_find_tags + \
                                                                 title_topic_model_tags + \
                                                                 body_topic_model_tags)
            predicted_tags['intersection'] = collections_utils.intersect_list([title_tags,
                                                                               tfidf_tags,
                                                                               code_import_tags,
                                                                               code_find_tags,
                                                                               title_topic_model_tags,
                                                                               body_topic_model_tags])
            col.update({'_id': item['_id']},
                       {'$set': {'predicted_tags': predicted_tags}})

            if idx % 1000 == 0:
                print(idx)


def score():
    db = mongodb_utils.get_connection()
    col = db['python_standard_test']

    with col.find(no_cursor_timeout=True) as items:
        for idx, item in enumerate(items):
            predicted_tags = item['predicted_tags']
            all_tag = predicted_tags['all']
            tag_list = item['Tag']
            title=item['question_Title']
            answer_plain_text = get_plain_text(item["answer_Text"])
            question_plain_text = get_plain_text(item["question_Body"])
            plain_text = answer_plain_text + " " + question_plain_text+" "+ title
            word_list=text_simple_process(plain_text)
            tag_list = [label.lower() for label in tag_list]
            tag_list=[label for label in tag_list if label in word_list]
            if len(tag_list)>0:
                recall_score=recall(tag_list,all_tag)
                col.update({'_id': item['_id']},
                       {'$set': {'recall_score': recall_score}})
            else:
                continue
            if idx % 1000 == 0:
                print(idx)



def recall(manual_tag_list, all_recommend_tags):
    cover_tags_sum = 0
    for manual_tag in manual_tag_list:
        for recommend_tag in all_recommend_tags:
            if recommend_tag in manual_tag or manual_tag in recommend_tag:
                cover_tags_sum += 1
                break
    return cover_tags_sum / len(manual_tag_list)


if __name__ == '__main__':
    score()
