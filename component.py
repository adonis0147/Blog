#!/usr/bin/env python
#-*- coding:utf-8 -*-
from math import ceil


class Paginator(object):
    def __init__(self, objects, number):
        self.count = len(objects)
        self.page_pages = int(ceil(float(self.count) / number))
        self.page_range = range(1, self.page_pages + 1)
        self.objects = objects
        self.number = number

    def page(self, index):
        try:
            index = min(max(index, self.page_range[0]), self.page_range[-1])
        except:
            index = 0
        start = (index - 1) * self.number
        end = index * self.number
        return self.Page(index, self.objects[start:end], self.page_range)

    class Page(object):
        def __init__(self, index, objects, page_range):
            self.__page_range = page_range

            self.index = index
            self.object_list = objects

        def has_next(self):
            return (self.index + 1) in self.__page_range

        def has_previous(self):
            return (self.index - 1) in self.__page_range

        def next_page_number(self):
            if self.has_next():
                return self.index + 1
            else:
                raise IndexError('Page index out of range')

        def previous_page_number(self):
            if self.has_previous():
                return self.index - 1
            else:
                raise IndexError('Page index out of range')
