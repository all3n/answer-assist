#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from collections import namedtuple
from terminaltables import AsciiTable
from six.moves import xrange
import codecs
QA = namedtuple('QA', ['question', 'answer','right'])


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
    assert(len(sens_list) > choice)
    q = "".join(clean_list(sens_list[:-choice]))
    a = clean_list(sens_list[-choice:])

    qa = QA(q,a,right)
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

