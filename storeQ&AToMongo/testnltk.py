import nltk
import pip
import re
# def filter_word(item):
#     return item[1]=='NN'
# # print(pip.pep425tags.get_supported())
# # nltk.download()
# texts_tokenized=['good', 'free', 'wysiwyg', 'editor', 'html', 'django', 'templat', "i'm", 'free', 'wysiwyg', 'html', 'editor', 'compat', 'django', 'templat', 'idea', 'blockquot', 'thank', 'lainmh', 'afraid', 'fckeditor', 'web', 'app', 'purpos', 'html', 'editor', 'html', 'django', 'compat', 'hope', 'issu', 'blockquot', 'brief', 'person', 'experi', 'python', 'develop', 'pydev', 'pydev', 'django', 'would', 'aptana', 'usabl', 'django', 'templat', 'complet', 'guid', 'link', 'help', 'hope']
# tagged = nltk.pos_tag(texts_tokenized)
# print(tagged)
# tagged_filter = filter(filter_word, tagged)
# tokens_filter = list(map(lambda item: item[0], tagged_filter))
# print(nltk.pos_tag(tokens_filter))


def check_split_word(str):
        codemode = re.compile(r'<（\S）*>([\s\S]*.)</（\S）*>')
        tag=False
        # print(text)
        if(str.find(".")):
            str_list=str.split(".")
        if(str_list[1]==str_list[1].capitalize( )):
            tag=True
            return tag,str_list
        else:
            return tag,str


tag,str=check_split_word('china.Evil')
print(tag,str)
tag,str=check_split_word('china.evil')
print(tag,str)