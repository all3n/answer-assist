#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class base_device(object):
    def __init__(self):
        pass

    def get_screen(self):
        raise NotImplementedError("NOT Impl get_screen")
