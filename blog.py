#!/usr/bin/env python
#-*- coding:utf-8 -*-
import tornado.database
import tornado.httpserver
import tornado.web
import tornado.ioloop
import os.path
import re
from model import Article, Label
from tornado.options import define, options

define("port", default=8888, type=int)
define("mysql_host", default="127.0.0.1:3306")
define("mysql_database", default="myblog")
define("mysql_user", default="myblog")
define("mysql_password", default="myblog")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/createArticle', CreateArticleHandler)
        ]
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            template_path=os.path.join(os.path.dirname(__file__), 'templates')
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = tornado.database.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password
        )


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class HomeHandler(BaseHandler):
    def get(self):
        articles = Article.all(self.db)
        self.render('index.html', articles=articles)


class CreateArticleHandler(BaseHandler):
    def get(self):
        self.render('createArticle.html')

    def post(self):
        title = self.get_argument('title')
        content_md = self.get_argument('content')
        pattern = r'\[[^\[\]]+\]'
        labels = re.findall(pattern, self.get_argument('labels'))

        if self.isNotNULL(title, content_md, labels):
            content_html = content_md

            article_id = Article.create(self.db, title, content_md, content_html)
            for label in labels:
                detail = label[1:-1]
                Label.create(self.db, article_id, detail)

            self.redirect('/', permanent=True)

    def isNotNULL(self, title, content_md, labels):
        return len(title) and len(content_md) and len(labels)


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
