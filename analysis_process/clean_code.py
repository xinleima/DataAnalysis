import re
import sys
import urllib.request
import nltk.stem



english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', '<', '>','=','/','--','{','}','< /']
bad_code_word=['/code', 'code', 'ul', '/ul', 'li', '/li', 'b', '/b', 'p', '/p', 'n\'t', "\'\'", "/pre", "pre", "\'", "``", "\'s", "\'m", 'use', '=']
bad_noun_word=['data','it','item','example','id','user','name','max_length','text','false','default','us','dev','task','block','code','detail','comment','e.g','em','strong']
codemode = re.compile(r'<pre><code>([\s\S]*?)</code></pre>')
linkmode=re.compile(r'<a href=\"([\s\S]*?)">')
patternCode = re.compile(r'<p>|</p>|<a.*?>([\s\S]*?)</a>|<img.*?>')
#匹配注释
commentmode=re.compile(r"[^']?#([\s\S]*?)\n")
#匹配doc
docmode=re.compile(r'\"\"\"([\s\S]*?)\"\"\"')
#匹配引进的库
import_library_mode=re.compile(r'from ([\s\S]*?)import ([\s\S]*?)\n')
# self.pattern = r"""(?x)     # 设置以编写较长的正则条件
# |\w+(?:[\.]\w+)*       # 用.链接的词汇
# |(?:[A-Z]\.)+          # 缩略词
# |\$?\d+(?:\.\d+)?%?    # 货币、百分数
# |\w+(?:[-']\w+)*       # 用连字符链接的词汇
# |\.\.\.                # 省略符号
# |(?:[.,;"'?():-_`])    # 特殊含义字符
#
# """
pattern =r"""\w+(?:[\.]\w+)*|(?:[A-Z]\.)+|\$?\d+(?:\.\d+)?%?|\w+(?:[-']\w+)*|\.\.\|(?:[.,;"'?():-_`])"""

#过滤出名词
def filter_word(item):
    # return (not item[1].startswith('V')) and (item[1] != 'IN') and (item[1] != '.') and (item[1] != 'RB')
    return item[1]=='NN'


 #判断“.”两端的词是否需要拆分
def check_split_word(str):
    codemode = re.compile(r'<（\S）*>([\s\S]*.)</（\S）*>')
    tag=False
    str_list=[]
    # print(text)
    if(str.find(".")):
        str_list=str.split(".")
        if(len(str_list)>1):
            check_str=str_list[len(str_list)-1].strip()
            if(check_str==check_str.capitalize( )):
                tag=True
                str_list=[str.replace('.'+str_list[len(str_list)-1],''),check_str]
                return tag,str_list
    return tag,str

def clean_code_label(code):
    code=code.replace("<br>","\n")
    code=code.replace("&gt;","")
    return code