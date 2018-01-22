#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from six.moves import urllib
from six.moves.urllib import parse
from bs4 import BeautifulSoup
from multiprocessing import Pool
import codecs
import sys
import re
from six.moves import range
reload(sys)
sys.setdefaultencoding("utf-8")
from termcolor import colored
from .search_engine import search_engine

line_split = "=" * 50
SPACE = re.compile("\s+")

# 爱问
BEST_ANSWER=u'最佳答案'

class baidu_qe(search_engine):
    def get_url_template(self):
        return "https://www.baidu.com/s?ie=utf-8&wd="

    def parse_answer(self,soup):
        search_result = soup.find("div", id="content_left")
        if not search_result:
            return

        op = search_result.find("div",{"class":"result-op"})
        op_type = ''
        op_val = ''

        if op:
            (op_type,op_val) = self.process_op(op)

        #if self.vote:
        #    return

        answers = search_result.find_all("div", {"class": "result"})[:self.top_n]

        for at in answers:
            # title
            title = at.find("h3",{"class","t"})
            if title:
                title = self.clean_res(title.text)
                print(u"title:%s" % (title))
            content = at.find("div",{"class","c-abstract"})
            if content:
                [s.extract() for s in content(['a'])]
                clean_txt = self.clean_res(content.text)
                if not clean_txt:
                    continue
                v = 1
                if BEST_ANSWER in clean_txt:
                    clean_txt = clean_txt.replace(BEST_ANSWER,colored(BEST_ANSWER,"red"))
                    v = 5
                for i in range(len(self.a)):
                    self.count_freq(clean_txt,i,v)
                    clean_txt = clean_txt.replace(self.a[i],colored(self.a[i],"red"))

                print(u"content:%s" % (clean_txt))
            print("---------------------------------------")
        if op_type and op_val:
            for i in range(len(self.a)):
                self.count_freq(op_val,i,10)
            print("%s,%s" % (colored(op_type,"green"),colored(op_val,"red")))

    def process_op(self,op):
        tpl = op.attrs["tpl"]
        print("find baidu op:%s" % (tpl))
        ret = ""
        if tpl == 'best_answer':
            ans = op.find("div",{"class":"op_best_answer_content"})
            ret = ans.text.strip()
        elif tpl == 'exactqa':
            ans = op.find("div",{"class":"op_exactqa_s_answer"})
            ret = ans.text.strip()
        elif tpl == 'exactqa_detail':
            ans = op.find("div",{"class":"op_exactqa_detail_s_answer"})
            ret = ans.text.strip()
        elif tpl == 'exactqa_family':
            ans = op.find("div",{"class":"op_exactqa_family_s_answer"})
            ret = ans.text.strip()
        elif tpl == 'calculator_html':
            ans = op.find("div",{"class":"op_new_val_screen_result"})
            ret = ans.text.strip()
        elif tpl == 'bk_polysemy':
            ans = op.find("div",{"class":"c-span-last"}).find("p")
            ret = ans.text.strip()
        return (tpl,ret)



if __name__ == '__main__':
    import sys
    sys.path.append("..")
    from question import *

    with codecs.open(sys.argv[1],"r","utf-8") as f:
        lines = f.readlines()
    qa = gen_qa(lines)

    qe = baidu_qe()
    qe.resolve(qa)


