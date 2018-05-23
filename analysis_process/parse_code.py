import ast
import os
import re

from get_lib_list import get_standard_list, get_django_list
from get_python_lib import get_standard_lib, get_django_lib

MAX_PACKAGE_INCLUDES = 5
MAX_CHILD_DEEP = 0.8


def __parse_import(code_str):
    re_import = re.compile(r'from ([\s\S]*?) import ([\s\S]*?)\n|import ([\s\S]*?)\n')
    import_list = re_import.findall(code_str)

    import_packages = []
    for imp in import_list:
        if imp[0] and imp[1]:
            pkgs = imp[1].replace(' ', '').replace('\n', '').split(',')
            import_packages += ["%s.%s" % (imp[0], pkg) for pkg in pkgs]
        else:
            pkgs = imp[2].replace(' ', '').replace('\n', '').split(',')
            import_packages += pkgs
    return import_packages


def __get_re_result(re_results):
    if not re_results:
        return None
    if re_results[0]:
        return re_results[0]
    if re_results[2]:
        return re_results[2]
    if re_results[4]:
        return re_results[4]
    return None


def depulicate(items):
    visitedItem = {}
    for item in items:
        visitedItem[item] = True
    return list(visitedItem.keys())


def __parse_call(code_str):
    # except ImportError: -

    # groups = []
    # groups.append(list(g))

    # os.name -

    # open (locfile, "rb")-

    # os.environ['PY_USE_XMLPLUS']-

    # sys.platform.startswith

    # 重复import -
    import_packages = []

    re_call = r'(\w+(\.\w+)*)[ ]*[([]|(\w+(\.\w+)+)|except (\w+)'

    #     re_call = r'(\w+(\.\w+)+)'

    code_lines = code_str.split('\n')
    for code_line in code_lines:
        match_result_list = re.findall(re_call, code_line)
        import_packages += [__get_re_result(match_result) for match_result in match_result_list]

    return depulicate(import_packages)


def parse_code(code_str):
    has_import = True
    import_packages = __parse_import(code_str)
    if len(import_packages) <= 0:
        has_import = False
        import_packages = __parse_call(code_str)
    return import_packages, has_import


__standard_lib = get_standard_list()
__django_lib = get_django_list()


def __including_call(pkg, call):
    if pkg.find("." + call + ".") != -1:
        return True
    if pkg.startswith(call + "."):
        return True
    if pkg.endswith("." + call):
        return True
    return pkg == call


def get_max_deep(string):
    # children = string.split('.')
    # deep_len = int(len(children) * MAX_CHILD_DEEP)
    # max_deep_children = children[: deep_len]
    # return '.'.join(max_deep_children)
    return string


def get_suffix_and_preffix(string):
    if not string:
        return string

    children = string.split('.')
    children_len = len(children)

    results = []
    for i in range(1, children_len):
        results.append('.'.join(children[0: i]))
        results.append('.'.join(children[i: children_len]))

    return results


def get_standard_packages(import_packages):
    standard_packages = {}
    for pkg in import_packages:
        cur_python_packages = {}
        match_self = None
        # item: [本身, 父级, 类型]
        for item in __standard_lib:
            if __including_call(item[0], pkg):
                if item[1] == 'built-in':
                    continue
                result = item[0]
                if result == pkg:
                    match_self = pkg
                if item[2] != 'model' and item[2] != 'class' and item[1] is not None:
                    result = item[1]
                if result:
                    cur_python_packages[get_max_deep(result)] = True
        if cur_python_packages:
            cur_python_package_list = list(cur_python_packages.keys())

            # 如果匹配到的数目多于MAX_PACKAGE_INCLUDES，就用 match_self
            standard_packages[pkg] = cur_python_package_list \
                if len(cur_python_package_list) <= MAX_PACKAGE_INCLUDES \
                else [match_self]

    return standard_packages


def get_django_packages(import_packages):
    django_packages = {}
    for pkg in import_packages:
        cur_django_packages = {}
        for item in __django_lib:
            if __including_call(item[0], pkg):
                result = item[0]
                if item[2] != 'model' and item[2] != 'class' and item[2] != 'built-in' and item[1] is not None:
                    result = item[1]
                if result:
                    cur_django_packages[get_max_deep(result)] = True
        if cur_django_packages:
            django_packages[pkg] = list(cur_django_packages.keys())
    return django_packages


def __filter_none_import_packages(packages):
    filtered_packages = {}
    for key, value in packages.items():
        if len(value) <= MAX_PACKAGE_INCLUDES:
            filtered_packages[key] = value
    return filtered_packages


def get_code_import_packages(code, has_django=False):
    import_packages, has_import = parse_code(code)

    if has_import:
        return import_packages, has_import

    standard_packages = get_standard_packages(import_packages)

    sub_import_packages = []
    for pkg in import_packages:
        if pkg not in standard_packages:
            sub_import_packages += get_suffix_and_preffix(pkg)
    sub_packages = get_standard_packages(sub_import_packages)
    standard_packages.update(sub_packages)

    standard_packages = __filter_none_import_packages(standard_packages)

    result = {}
    result.update(standard_packages)

    if has_django:
        django_packages = get_django_packages(import_packages)
        django_packages = __filter_none_import_packages(django_packages)
        result.update(django_packages)

    # result: {'os.mkdir': ['os']}
    item_list = []
    for value in result.values():
        item_list += value

    return item_list


if __name__ == '__main__':
    def main():
        # code_str = """HttpResponse("Hello, world. You're at the polls index.")\nsys('test')"""
        # print(get_code_import_packages(code_str))
        #
        # code_str = """import sys\nimport a.c\nfrom d import m, n"""
        # print(get_code_import_packages(code_str))
        # code_str = """print(os.name)"""
        # print(get_code_import_packages(code_str))
        # __parse_import(code_str)
        code_str = 'path.join()\na.b()\nset()'
        print(get_code_import_packages(code_str))


    main()
