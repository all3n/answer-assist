#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from collections import namedtuple
from terminaltables import AsciiTable
from six.moves import xrange
import codecs
QA = namedtuple('QA', ['question', 'answer','answer_tokens','right'])
import re
import jieba


QA_INDEX_PATTERN = re.compile("\d+/\d+")


def clean(s):
    return s.strip().replace(u"《".encode("utf-8"),"").replace(u"》".encode("utf-8"),"")

def clean_list(l):
    return map(lambda x:clean(x),l)



def question_pre_process(qs):
    now = datetime.today()


def load_qa_from_file(f):
    with codecs.open(f,"r","utf-8") as qaf:
        lines = qaf.readlines()
        return gen_qa(lines[:-1],right=int(lines[-1]))
    return None


def gen_qa(sens_list,choice=3,right=-1):
    print "\n".join(sens_list)
    assert(len(sens_list) > choice)

    # TODO remove question index num like 1/12
    last = sens_list[-1]
    if QA_INDEX_PATTERN.match(last):
        sens_list = sens_list[:-1]

    q = "".join(clean_list(sens_list[:-choice]))
    a = clean_list(sens_list[-choice:])
    answer_tokens = map(lambda x:jieba.cut(x),a)



    qa = QA(q,a,answer_tokens,right)
    print_qa(qa)
    return qa


def print_qa(qa):
    table_data = [
        ['question', qa.question],
    ]
    for i in xrange(len(qa.answer)):
        table_data.append([i+1,qa.answer[i]])
    if qa.right != -1:
        table_data.append(['right',qa.right])
    table = AsciiTable(table_data)
    table.inner_row_border = True
    print(table.table)

