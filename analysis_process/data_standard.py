import re
import csv

from bs4 import BeautifulSoup

from utils.mongodb_utils import get_connection


def get_collection_all_data(conn, collection):
    db_collection = conn[collection]
    return db_collection.find()


def standard_data(input_body):
    """对原始的question/answer的body进行预处理.

    :param input_body: str. 输入question/answer的body.
    """
    # re_code_mode = re.compile(r'<pre><code>([\s\S]*?)</code></pre>')
    # re_link_mode = re.compile(r'<a href=\"([\s\S]*?)">')
    # re_html_mode = re.compile(r'<p>|</p>|<a.*?>([\s\S]*?)</a>|<img.*?>')
    #
    # input_body = input_body.replace('<blockquote>', '').replace('</blockquote>', '')
    #
    # codes = re_code_mode.findall(input_body)
    # links = re_link_mode.findall(input_body)
    #
    # answer_plain_text = re_html_mode.sub('', input_body)
    # if codes:
    #     answer_plain_text = re_code_mode.sub('', answer_plain_text)
    # if links:
    #     answer_plain_text = re_link_mode.sub('', answer_plain_text)
    # answer_plain_text.replace('\n', '')
    #
    # return codes, links, answer_plain_text
    soup = BeautifulSoup(input_body, 'lxml')

    raw_codes = soup.select('pre code')
    for raw_code in raw_codes:
        for br_tag in raw_code.find_all('br'):
            br_tag.replace_with('\n')
    codes = [raw_code.get_text(' ') for raw_code in raw_codes]

    raw_links = soup.find_all('a')
    links = [raw_link.get('href') for raw_link in raw_links]

    for tag in soup.select('pre code, a'):
        tag.extract()
    plain_text = soup.get_text(' ')

    return codes, links, plain_text


def standard_db_data(collection_name):
    conn = get_connection()
    collection = conn[collection_name]
    cnt = 0
    # 匹配代码
    re_code_mode = re.compile(r'<pre><code>([\s\S]*?)</code></pre>')
    # 匹配链接
    re_link_mode = re.compile(r'<a href=\"([\s\S]*?)">')
    re_html_mode = re.compile(r'<p>|</p>|<a.*?>([\s\S]*?)</a>|<img.*?>')

    objs = []
    data_collection = collection.find()

    for data in data_collection:
        obj = data

        answer_body = data["answer_Body"].replace("<blockquote>", "").replace("</blockquote>", "")

        codes = re_code_mode.findall(answer_body)
        links = re_link_mode.findall(answer_body)
        answer_plain_text = re_html_mode.sub('', answer_body)

        if codes:
            answer_plain_text = re_code_mode.sub('', answer_plain_text)
        if links:
            answer_plain_text = re_link_mode.sub('', answer_plain_text)
        answer_plain_text.replace('\n', '')
        obj["answer_Text"] = answer_plain_text
        obj["answer_Code"] = codes
        obj["answer_Link"] = links
        objs.append(obj)

    for obj in objs:
        collection.update({"_id": obj["_id"]}, {
            "$set": {"answer_Code": obj["answer_Code"], "answer_Link": obj["answer_Link"],
                     "answer_Text": obj["answer_Text"]}})
        if cnt % 1000 is 0:
            print('insert into %s: %d' % (collection_name, cnt))
        cnt += 1


# 在数据中提取出代码部分
# 以及链接到别的问题的链接
def data_standard_to_db(db, filename, collection_name):
    row_sum = 0
    cnt = 0
    # 匹配代码
    codemode = re.compile(r'<pre><code>([\s\S]*?)</code></pre>')
    # 匹配链接
    linkmode = re.compile(r'<a href=\"([\s\S]*?)">')
    patternCode = re.compile(r'<p>|</p>|<a.*?>([\s\S]*?)</a>|<img.*?>')
    objs = []
    with open(filename, 'r', encoding='utf-8', errors="replace") as fin:
        reader = csv.reader(fin)
        header = None

        for row in reader:
            if cnt >= 41010:
                break

            if cnt % 1000 is 0:
                print('insert into %s: %d/%d' % (collection_name, cnt, row_sum))
            if header is None:
                header = row
            else:
                obj = {}
                cnt += 1
                for i in range(0, len(header)):
                    obj[header[i]] = row[i]
                # if 'Body' in obj:
                obj['Body'] = obj['Body'].replace("<blockquote>", "")
                obj['Body'] = obj['Body'].replace("</blockquote>", "")
                # 找到代码部分，存放在list里面
                has_code = codemode.findall(obj['Body'])
                # 找到链接部分，存放在list里面
                has_link = linkmode.findall(obj['Body'])
                # 新增code字段
                obj["answer_Code"] = has_code
                # 新增link字段
                obj["answer_Link"] = has_link
                # 新增text字段，保存非代码的文本部分
                obj["answer_Text"] = patternCode.sub("", obj["Body"])
                # 将body除去代码字段,得到文本字段
                if has_code:
                    # 文本部分除去代码
                    obj["answer_Text"] = codemode.sub("", obj["answer_Text"])
                if has_link:
                    obj["answer_Text"] = linkmode.sub("", obj["answer_Text"])
                # 文本部分除去换行
                obj["answer_Text"] = obj["answer_Text"].replace("\n", "")
                # print(cnt)
                # print(obj["answer_Code"])
                # print(obj["answer_Link"])
                # print(obj["answer_Text"])
                objs.append(obj)
    cnt = 0
    for obj in objs:
        db[collection_name].update({"answer_Id": obj["Id"]}, {
            "$set": {"answer_Code": obj["answer_Code"], "answer_Link": obj["answer_Link"],
                     "answer_Text": obj["answer_Text"]}})
        if cnt % 1000 is 0:
            print('insert into %s: %d' % (collection_name, cnt))
        cnt += 1
    fin.close()


# 根据filter在数据库中批量增加字段
# add_filed 在数据库中增加的字段 类型为string
# filter_filed在数据库中过滤的字段 类型为string
# filter 过滤条件的名称，对应于数据库中过滤字段，csv文件中字段 类型为string
def append_tag_field_indb(self, db, collection_name, add_filed, filter_filed, filter):
    db_collection = db[collection_name]
    row_sum = 0
    # django_tags_id_list = []
    # django_id_list=[]
    django_answer_list = []
    django_qusetios_list = []
    django_parent_id = []
    django_question_title = []
    django_question_body = []
    count = 0
    # with open(django_tags_filename, 'r', encoding='utf-8', errors="replace") as fin:
    #     reader = csv.reader(fin)
    #     header = None
    #     cnt = 0
    #     for row in reader:
    #         if cnt % 10000 is 0:
    #             print('has read data %s: %d/%d' % (collection_name, cnt, row_sum))
    #         cnt += 1
    #         if header is None:
    #             header = row
    #         else:
    #             obj = {}
    #             for i in range(0, len(header)):
    #                 obj[header[i]] =row[i]
    #             django_id_list.append(obj["Id"])
    #             django_tags_id_list.append(obj)
    #     fin.close()
    for item in list(db['django_questions'].find()):
        django_qusetios_list.append(item)
        django_parent_id.append(item["Id"])
        django_question_title.append(item["Title"])
        django_question_body.append(item["Body"])

    for item in list(db['django_answers'].find()):
        django_answer_list.append(item)

        # for obj in django_tags_id_list:
        #     if count % 1000is 0:
        #         print('has update data %s: %d/%d' % (collection_name, count, row_sum))
        #     count += 1
        #     # id=obj["Id"]
        #     # tag=obj["Tag"]
        #     Filter=obj[filter]
        #     Add_filed=obj[add_filed]
        # if count<5:
        # print(list(db[collection_name].find({filter_filed:Filter})))
        # 找到对应的object增加字段，注意如果筛选条件对应多个object都要进行操作要加multi=True

    # for obj in django_answer_list:
    #     count+=1
    #     if count % 1000 is 0:
    #          print('has read data %s: %d' % (collection_name, count))
    #     db[collection_name].update({"Id":obj["Id"]},{"$set":{"Body":obj["Body"]}},multi=True)

    for obj in django_qusetios_list:
        count += 1
        if count % 1000 is 0:
            print('has read data %s: %d' % (collection_name, count))
        Filter = obj[filter]
        Add_filed_title = obj["Title"]
        Add_filed_body = obj["Body"]
        db[collection_name].update({filter_filed: Filter}, {"$set": {add_filed[1]: Add_filed_body}}, multi=True)
        # print(list(db[collection_name].find({"ParentId":obj["Id"]})))
        # db[collection_name].update({filter_filed:Filter},{"$set":{add_filed[1]:Add_filed_body}},multi=True)


def modify_filed_name(self, db, collection_name, old_filedname_list, new_filedname_list):
    for index in range(len(old_filedname_list)):
        db[collection_name].update({}, {"$rename": {old_filedname_list[index]: new_filedname_list[index]}}, multi=True)


if __name__ == '__main__':
    def main():
        # standard_db_data('python_standard_has_code')
        html = """<p>I've read that it is possible to add a method to an existing object (e.g. not in the class definition) in <strong>Python</strong>, I think this is called <em>Monkey Patching</em> (or in some cases <em>Duck Punching</em>). I understand that it's not always a good decision to do so. But, how might one do this?</p>\n\n<p><strong>UPDATE 8/04/2008 00:21:01 EST:</strong></p>\n\n<p><a href=\"http://stackoverflow.com/a/982\">That</a> looks like a good answer John Downey, I tried it but it appears that it ends up being not a <em>true</em> method.</p>\n\n<p>Your example defines the new patch function with an argument of <strong><code>self</code></strong>, but if you write actual code that way, the now patched class method asks for an argument named <code>self</code> (it doesn't automagically recognize it as the object to which it is supposed to bind, which is what would happen if defined within the class definition), meaning you have to call <strong><code>class.patch(obj)</code></strong> instead of just <strong><code>class.patch()</code></strong> if you want the same functionality as a <em>true</em> method.</p>\n\n<p><strong>It looks like Python isn't really treating it as a method, but more just as a variable which happens to be a function</strong> (and as such is callable).  Is there any way to attach an actual method to a class?</p>\n\n<p>Oh, and Ryan, <a href=\"http://pypi.python.org/pypi/monkey\">that</a> isn't exactly what I was looking for (it isn't a builtin functionality), but it is quite cool nonetheless.</p>\n"""
        print(standard_data(html))


    main()
