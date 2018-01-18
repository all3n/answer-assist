#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from six.moves import urllib
from six.moves.urllib import parse
from bs4 import BeautifulSoup
from multiprocessing import Pool
import codecs
import sys
from six.moves import range
from .search_engine import search_engine
reload(sys)
sys.setdefaultencoding("utf-8")
from termcolor import colored

line_split = "=" * 50


class sogou_qe(search_engine):

    def get_url_template(self):
        return "https://www.sogou.com/web?query="

    def parse_answer(self,soup):
        search_result = soup.find("div", {"class": "results"})
        answers = search_result.find_all("div", {"class": "vrwrap"})[:self.top_n]

        for at in answers:
            # title
            title = at.find("h3",{"class","vrTitle"})
            if title:
                title = self.clean_res(title.text)
                print(u"title:%s" % (title))
            content = at.find("div",{"class","strBox"})
            if content:
                clean_txt = self.clean_res(content.text)
                if not clean_txt:
                    continue
                for i in range(len(self.a)):
                    self.count_freq(clean_txt,i)
                    clean_txt = clean_txt.replace(self.a[i],colored(self.a[i],"red"))

                print(u"content:%s" % (clean_txt))
            print("---------------------------------------")



if __name__ == '__main__':
    import sys
    sys.path.append("..")
    from question import *

    with codecs.open(sys.argv[1],"r","utf-8") as f:
        lines = f.readlines()
    qa = gen_qa(lines)

    qe = sogou_qe()
    qe.resolve(qa)


