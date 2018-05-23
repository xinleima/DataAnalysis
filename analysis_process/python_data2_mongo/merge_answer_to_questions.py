import re

from utils.mongodb_utils import get_connection


def get_collectoin_all_data(conn, collection):
    db_collection = conn[collection]
    return db_collection.find()


def count_hascode():
    count = 0
    conn = get_connection()
    collection = conn['python_answers_with_question']
    data_collection = collection.find()
    for data in data_collection:
        has_code = data["answer_Code"]
        if has_code:
            count += 1
    print(count)


def select_hascode():
    codemode = re.compile(r'<pre><code>([\s\S]*?)</code></pre>')
    count = 0
    conn = get_connection()
    collection = conn['python_standard']
    has_code_list = []
    data_collection = collection.find()
    for data in data_collection:
        has_code = codemode.findall(data["answer_Body"])
        if has_code:
            has_code_list.append(data)
            count += 1
        if count % 1000 is 0:
            print('insert into %d' % (count))
    print(count)
    new_collection = conn['python_standard_has_code']
    new_collection.insert(has_code_list)


# 存在一个问题对应多个tag，原来只find一个，重新找tag
def update_answer_tag(answer_collection_name='python_answers_with_question',
                      tag_collection_name='python_tags'):
    conn = get_connection()
    answer_collection = conn[answer_collection_name]
    tag_collection = conn[tag_collection_name]

    answers = answer_collection.find(no_cursor_timeout=True)

    tags_scan = tag_collection.find()
    map_question_id_to_tags = {}
    for tag in tags_scan:
        question_id = tag['Id']
        if not question_id in map_question_id_to_tags:
            question_tags = []
            map_question_id_to_tags[question_id] = question_tags
        else:
            question_tags = map_question_id_to_tags[question_id]

        question_tags.append(tag['Tag'])

    total = answer_collection.count()
    count = 0

    for answer in answers:
        question_id = answer['question_Id']
        tags = map_question_id_to_tags[question_id]

        answer_collection.update(
            {'_id': answer['_id']},
            {'$set': {
                'Tag': tags
            }}
        )

        count += 1
        print("%s/%s" % (count, total))

    answers.close()


# python问题，回答和tag数据集整合
def get_merged_questions():
    conn = get_connection()
    question_db = conn['python_questions']
    answer_db = conn['python_answers']
    tag_db = conn['python_tags']
    answer_with_question_db = conn['python_standard']

    answers = answer_db.find(no_cursor_timeout=True)

    buffer = []
    buffer_size = 1000
    cur_buffer_size = 0
    total = 0

    for answer in answers:
        question_id = answer['ParentId']
        question = question_db.find_one({"Id": question_id})

        result = {'answer_Id': answer['Id'], 'answer_OwnerUserId': answer['OwnerUserId'],
                  'answer_CreationDate': answer['CreationDate'], 'answer_Score': answer['Score'],
                  'answer_Body': answer['Body']}

        if question:
            result['question_Id'] = question['Id']
            result['question_OwnerUserId'] = question['OwnerUserId']
            result['question_CreationDate'] = question['CreationDate']
            result['question_Score'] = question['Score']
            result['question_Title'] = question['Title']
            result['question_Body'] = question['Body']

        tag = tag_db.find_one({"Id": question_id})
        if tag:
            result['Tag'] = tag['Tag']

        buffer.append(result)

        cur_buffer_size += 1
        if cur_buffer_size >= buffer_size:
            total += cur_buffer_size
            print(total)
            answer_with_question_db.insert(buffer)
            cur_buffer_size = 0
            buffer.clear()

    answers.close()


if __name__ == '__main__':
    # get_merged_questions()
    # update_answer_tag()
    # count_hascode()
    # select_hascode()
    update_answer_tag(answer_collection_name='python_standard_has_code')
