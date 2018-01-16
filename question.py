#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from collections import namedtuple
QA = namedtuple('QA', ['question', 'answer'])


def clean(s):
    return s.strip().replace(u"《".encode("utf-8"),"").replace(u"》".encode("utf-8"),"")

def clean_list(l):
    return map(lambda x:clean(x),l)



def question_pre_process(qs):
    now = datetime.today()



def gen_qa(sens_list,choice=3):
    assert(len(sens_list) > choice)

    q = "".join(clean_list(sens_list[:-choice]))

    a = clean_list(sens_list[-choice:])

    return QA(q,a)

