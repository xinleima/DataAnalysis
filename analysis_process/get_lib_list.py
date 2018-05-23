import re

from bs4 import BeautifulSoup

from utils.file_utils import read_file_to_string


def _get_hash_of_href(href):
    match_result = re.match(r'^.*#(.*)$', href)
    if match_result:
        return match_result.group(1)
    return match_result


def _is_valid_hash(href_hash):
    return href_hash is not None and not re.match(r'^index-\d+$', href_hash)


def get_parent(child_text):
    if re.match(r'^\w+$', child_text):
        return child_text, 'unknown'

    # AsyncIterator (class in collections.abc)
    if re.findall(r'\(class in [\w.]+\)', child_text):
        return child_text, 'class'

    # add_alias() (in module email.charset)
    match_result = re.findall(r'[\w.]+\(\) \(in module ([\w.]+)\)', child_text)
    if match_result:
        return match_result[0], 'module_method'

    # add_alias (in module email.charset)
    match_result = re.findall(r'\(in module ([\w.]+)\)', child_text)
    if match_result:
        return match_result[0], 'module_attribute'

    # combine() (datetime.datetime class method)
    match_result = re.findall(r'\(([\w.]+) class method\)', child_text)
    if match_result:
        return match_result[0], 'class_static_method'

    # add_alternative() (email.message.EmailMessage method)
    match_result = re.findall(r'\(([\w.]+) method\)', child_text)
    if match_result:
        return match_result[0], 'method'

    # _PyImport_Fini (C function)
    match_result = re.findall(r'\(([\w.-]+) function\)', child_text)
    if match_result:
        return match_result[0], 'function'

    # bytearray (built-in class)
    match_result = re.findall(r'\(([\w.-]+) class\)', child_text)
    if match_result:
        return match_result[0], 'class'

    # license (built-in variable)
    match_result = re.findall(r'\(([\w.-]+) variable\)', child_text)
    if match_result:
        return match_result[0], 'variable'

    # inquiry (C type)
    match_result = re.findall(r'\(([\w.-]+) type\)', child_text)
    if match_result:
        return match_result[0], 'type'

    # ALWAYS_TYPED_ACTIONS (optparse.Option attribute)
    match_result = re.findall(r'\(([\w.]+) attribute\)', child_text)
    if match_result:
        return match_result[0], 'attribute'

    # asyncio (module)
    match_result = re.findall(r'([\w.]+) \(module\)', child_text)
    if match_result:
        return match_result[0], 'module'

    return None, None


def get_parent_of_django(child_text):
    if re.match(r'^[\w.-]+$', child_text):
        return child_text, 'unknown'

    # abstract(Options attribute)
    match_result = re.findall(r'\(([\w.]+) attribute\)', child_text)
    if match_result:
        return match_result[0], 'attribute'

    # (class in django.contrib.auth.mixins)
    match_result = re.findall(r'\(class in ([\w.]+)\)', child_text)
    if match_result:
        return match_result[0], 'class'

    # activate() ( in module django.utils.timezone)
    match_result = re.findall(r'[\w.]+\(\) \(in module ([\w.]+)\)', child_text)
    if match_result:
        return match_result[0], 'module_method'

    # add_alias (in module email.charset)
    match_result = re.findall(r'\(in module ([\w.]+)\)', child_text)
    if match_result:
        return match_result[0], 'module_attribute'

    # add() (GeometryCollection method)
    match_result = re.findall(r'\(([\w.]+) method\)', child_text)
    if match_result:
        return match_result[0], 'method'

    # ArchiveIndexView (built-in class )
    match_result = re.findall(r'\(([\w.-]+) class\)', child_text)
    if match_result:
        return match_result[0], 'class'

    # _PyImport_Fini (C function)
    match_result = re.findall(r'\(([\w.-]+) function\)', child_text)
    if match_result:
        return match_result[0], 'function'

    # license (built-in variable)
    match_result = re.findall(r'\(([\w.-]+) variable\)', child_text)
    if match_result:
        return match_result[0], 'variable'

    # asyncio (module)
    match_result = re.findall(r'([\w.]+) \(module\)', child_text)
    if match_result:
        return match_result[0], 'module'

    return None, None


def get_standard_list():
    html_doc = read_file_to_string('./analysis_process/spider_lib_file/python_doc_index.html')
    soup = BeautifulSoup(html_doc, 'lxml')

    table_list = soup.find_all('table')

    link_list = []
    for table in table_list:
        anchor_list = table.find_all('a')
        for anchor in anchor_list:
            href = anchor.get('href')
            text = anchor.text
            href_hash = _get_hash_of_href(href)
            if _is_valid_hash(href_hash):
                parent, self_type = get_parent(text)
                link_list.append([href_hash, parent, self_type])

    return link_list


def get_django_list():
    html_doc = read_file_to_string('./analysis_process/spider_lib_file/django_doc_index.html')
    soup = BeautifulSoup(html_doc, 'lxml')

    anchor_list = soup.find_all('a')

    link_list = []
    for anchor in anchor_list:
        link = _get_hash_of_href(anchor.get('href'))
        if link and len(link) > 1 and link != 'Symbols':
            parent, self_type = get_parent_of_django(anchor.text)
            link_list.append([link, parent, self_type])

    return link_list


if __name__ == '__main__':
    for item in get_standard_list():
        if item[1] == 'built-in':
            print(item)
