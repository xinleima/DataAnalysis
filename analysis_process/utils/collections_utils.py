def reverse_key_value(_dict):
    """{key: value} 转化为 {value: key}."""
    return {v: k for k, v in _dict.items()}


def depulicate(_list):
    return list(set(_list))


def intersect_list(list_list):
    visited_word = dict()
    for _list in list_list:
        for word in _list:
            if word not in visited_word:
                visited_word[word] = 1
            else:
                visited_word[word] += 1

    return [key for key, value in visited_word.items() if value > 1]


def union_list(list_list):
    merged_set = set()
    for _list in list_list:
        merged_set = merged_set | set(_list)
    return list(merged_set)


def remove_empty(_list):
    return [item for item in _list if item]


if __name__ == '__main__':
    print(intersect_list([['string', 'array', 'checkbox', 'web.py'],
                          ['web.py', 'checkboxes', 'index.html'],
                          [],
                          ['built-in', 'fileinput']]))
