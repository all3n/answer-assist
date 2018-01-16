#!/usr/bin/env python


class ocr(object):
    def __init__(self,conf):
        self.conf = conf

    def detect_text(self,image_bytes):
        raise NotImplementedError("detect_text")
