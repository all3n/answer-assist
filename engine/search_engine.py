from bs4 import BeautifulSoup
import requests
from six.moves import urllib
from six.moves.urllib import parse
import re
from terminaltables import AsciiTable
from termcolor import colored

class search_engine(object):
    top_n = 5
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686)Gecko/20071127 Firefox/2.0.0.11'}

    def get_url_template(self):
        raise NotImplementedError("NOT Impl get url template")

    def query_by_url(self):
        url_base = self.get_url_template()
        url = url_base + parse.quote(self.q.encode('utf-8'))
        #url = url + "%20" + parse.quote(" ".join(self.a).encode('utf-8'))

        soup_res = BeautifulSoup(requests.get(url=url, headers=self.headers).content, "lxml")
        [s.extract() for s in soup_res(['script', 'style', 'img', 'sup', 'b'])]
        # print(soup.prettify())
        return soup_res


    def parse_answer(self,soup):
       raise NotImplementedError("NOT Impl parse_answer")

    def resolve(self,qa):
        self.q = qa.question
        self.a = qa.answer
        self.vote = {}
        soup = self.query_by_url()
        self.parse_answer(soup)
        self.print_res()

    def clean_res(self,s):
        return re.sub(u"\s+",u" ",s)

    def count_freq(self,txt,i,vote=1):
        if not txt:
            return
        c = txt.count(self.a[i]) * vote
        if c > 0:
            if i in self.vote:
                self.vote[i] += c
            else:
                self.vote[i] = c

    def print_res(self):
        res_tables = [['option','score','p']]
        total = sum(self.vote.values())
        if self.vote:
            right = max(self.vote,key=lambda x:self.vote[x])
            for x in range(len(self.a)):
                if x in self.vote:
                    res_tables.append([self.a[x],self.vote[x],(self.vote[x] * 100.0) /total])
                else:
                    res_tables.append([self.a[x],0,0])
            table = AsciiTable(res_tables)
            table.inner_column_border = True

            print(table.table)
            print("Suggest Answer:%d %s" % (right+1,colored(self.a[right],'yellow')))



