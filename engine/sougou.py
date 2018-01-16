#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from six.moves import urllib
from six.moves.urllib import parse
from bs4 import BeautifulSoup
from multiprocessing import Pool
import re
import codecs
import sys
from six.moves import range
reload(sys)
sys.setdefaultencoding("utf-8")
from termcolor import colored

line_split = "=" * 50


class sogou_qe(object):
    top_n = 3
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'}

    def sogou_search(self,question):
        prefix = 'https://www.sogou.com/web?query='
        url = prefix + parse.quote(question.encode('utf-8'))
        req = urllib.request.Request(url=url, headers=self.headers)
        res = urllib.request.urlopen(req, timeout=3)
        if res.getcode() != 200:
            print('search error, error code: ', res.getcode()  )
        return res.read().decode('utf-8')

    def resolve(self,q):
        self.q = qa.question
        self.a = qa.answer
        self.vote = {}
        #print "=================="
        #print self.q
        #print "|".join(self.a)

        self.parse_answer(self.sogou_search(self.q))

    def clean_res(self,s):
        return re.sub(u"\s+",u" ",s)

    def count_freq(self,txt,i):
        if not txt:
            return
        c = txt.count(self.a[i])
        if c > 0:
            if i in self.vote:
                self.vote[i] += c
            else:
                self.vote[i] = c


    def parse_answer(self,html):
        soup = BeautifulSoup(html, "lxml")
        search_result = soup.find("div", {"class": "results"})
        answers = search_result.find_all("div", {"class": "vrwrap"})

        for at in answers:
            # title
            title = at.find("h3",{"class","vrTitle"})
            if title:
                self.clean_res(title.text)
            content = at.find("div",{"class","strBox"})
            if content:
                clean_txt = self.clean_res(content.text)
                if not clean_txt:
                    continue
                for i in range(len(self.a)):
                    self.count_freq(clean_txt,i)
                    clean_txt = clean_txt.replace(self.a[i],colored(self.a[i],"red"))

                print clean_txt
            print "---------------------------------------"

        total = sum(self.vote.values())
        right = max(self.vote)
        for x in range(len(self.a)):
            if x in self.vote:
                print self.a[x]
                print(u"%s, %.2f %%" % (self.a[x],(self.vote[x] * 100.0) /total))
            else:
                print(u"%s,%.2f %%" % (self.a[x],0))
        print '------------------------------------------------'
        print(u"%d:%s" % (right,self.a[right]))


        # multi processors
        #pool = Pool(self.top_n)
        #res = pool.map(self._parser_single_answer, answers[:self.top_n])
        #pool.close()
        #pool.join()
        #for _res in res:
        #  if _res:
        #    print(_res)
        #print(line_split)



    def _parser_single_answer(answer):
        question_desc = answer.find("a", {"target": "_blank"})
        if not question_desc:
            return None
        answer_box = line_split
        answer_box += '\n'
        answer_box += '>>>'
        answer_box += high_light_question(''.join(map(str, question_desc.contents)))
        answer_box += '\n'
        texts = answer.find_all("div", {"class": "str-text-info"})
        for text in texts:
            text_str = str(text)
            if u'问题说明' in text_str:
                continue
            span = text.find("span")
            if not span:
                continue
            answer_desc = high_light_answer(''.join(map(str, span.contents)))
            if u'最佳答案' in text_str:
                answer_desc = u'最佳答案: %s' % answer_desc
            answer_box += answer_desc
        return answer_box


if __name__ == '__main__':
    import sys
    sys.path.append("..")
    from question import *

    with codecs.open(sys.argv[1],"r","utf-8") as f:
        lines = f.readlines()
    qa = gen_qa(lines)

    qe = sogou_qe()
    qe.resolve(qa)


