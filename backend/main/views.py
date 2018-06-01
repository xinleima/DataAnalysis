import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from bs4 import BeautifulSoup

from gen_tags import TagsGenerator
from utils import collections_utils

tags_generator = TagsGenerator()


def __add_code_tag(body):
    soup = BeautifulSoup(body, 'lxml')
    pre_tags = soup.find_all('pre')
    for pre_tag in pre_tags:
        code_tag = soup.new_tag('code')
        for child in pre_tag.children:
            removed_tag = child.extract()
            code_tag.append(removed_tag)
        pre_tag.append(code_tag)
    return str(soup)


@csrf_exempt
def post_tags(request):
    if request.method == 'POST':
        res_raw_data = request.body.decode('utf-8')
        res_json_data = json.loads(res_raw_data)

        title = res_json_data['title']
        body = __add_code_tag(res_json_data['body'])

        intersection_tags, \
        title_tags, \
        tfidf_tags, \
        code_import_tags, \
        code_find_tags, \
        title_topic_model_tags, \
        body_topic_model_tags = tags_generator.gen_tags(title, body)

        code_tags = collections_utils.depulicate(code_find_tags + code_import_tags)
        all_tags = collections_utils.depulicate(
            title_tags + tfidf_tags + title_topic_model_tags + body_topic_model_tags + code_tags)
        text_tags = [tag for tag in all_tags if tag not in intersection_tags]

        return JsonResponse({
            'code': code_tags,
            'text': text_tags,
            'intersection': intersection_tags
        })
    else:
        return JsonResponse({
            'msg': 200
        })
