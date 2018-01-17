#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from six.moves import urllib
from six.moves.urllib import parse
from bs4 import BeautifulSoup
from multiprocessing import Pool
import codecs
import sys
from six.moves import range
reload(sys)
sys.setdefaultencoding("utf-8")
from termcolor import colored
from search_engine import search_engine

line_split = "=" * 50

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
        if op:
            op_answer = op.find("div",{"class","op_exactqa_s_answer"})
            if op_answer:
                print(u"找到百度知识图谱")
                op_answer_txt = op_answer.text
                for i in range(len(self.a)):
                    self.count_freq(op_answer_txt,i,10)


        if self.vote:
            return

        answers = search_result.find_all("div", {"class": "result"})[:self.top_n]

        for at in answers:
            # title
            title = at.find("h3",{"class","t"})
            if title:
                title = self.clean_res(title.text)
                print(u"title:%s" % (title))
            content = at.find("div",{"class","c-abstract"})
            if content:
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
            print "---------------------------------------"

if __name__ == '__main__':
    import sys
    sys.path.append("..")
    from question import *

    with codecs.open(sys.argv[1],"r","utf-8") as f:
        lines = f.readlines()
    qa = gen_qa(lines)

    qe = baidu_qe()
    qe.resolve(qa)


