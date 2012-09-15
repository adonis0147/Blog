#!/usr/bin/env python
#-*- coding:utf-8 -*-
import tornado.database
import tornado.httpserver
import tornado.web
import tornado.ioloop
import os.path
import markdown
import ConfigParser
import re
from model import Article, Label, Auth, Search
from component import Paginator
from tornado.options import define, options


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/article/(\d+)', ArticleHandler),
            (r'/createArticle', CreateArticleHandler),
            (r'/preview', PreviewHandler),
            (r'/article/edit/(\d+)', EditArticleHandler),
            (r'/article/update/(\d+)', UpdateArticleHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/auth', AuthHandler),
            (r'/page/(\d+)', ArticleListHandler),
            (r'/search', SearchHandler),
        ]
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            autoescape=None,
            xsrf_cookies=True,
            cookie_secret='6de683f6e8f038f62863fe27a17573e5',
            login_url='/login',
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

    def write_error(self, status_code, **kwargs):
        if status_code == 400:
            error = "400: Bad Request"
            self.render('error.html', error=error, home_title=options.home_title)
        if status_code == 405:
            error = "405: Method Not Allowed"
            self.render('error.html', error=error, home_title=options.home_title)
        if status_code == 404:
            error = "404: Page Not Found"
            self.render('error.html', error=error, home_title=options.home_title)

    def get_current_user(self):
        return self.get_secure_cookie('user')

    def isAdmin(self):
        if self.get_secure_cookie('user'):
            return True
        else:
            return False


class HomeHandler(BaseHandler):
    def get(self):
        p = Paginator(Article.all(self.db), 5)
        page = p.page(1)
        isAdmin = self.isAdmin()
        label_list = Label.group(self.db)
        self.render('index.html', articles=page.object_list, label_list=label_list,
                isAdmin=isAdmin, page=page, home_title=options.home_title,
                user=options.user, photo=options.photo)


class ArticleListHandler(BaseHandler):
    def get(self, pageId):
        p = Paginator(Article.all(self.db), 5)
        page = p.page(int(pageId))
        isAdmin = self.isAdmin()
        label_list = Label.group(self.db)
        self.render('index.html', articles=page.object_list, label_list=label_list,
                isAdmin=isAdmin, page=page, home_title=options.home_title,
                user=options.user, photo=options.photo)


class ArticleHandler(BaseHandler):
    def get(self, id):
        article = Article.get(self.db, id)
        if article is None:
            error = '404: Page Not Found'
            self.render('error.html', error=error, home_title=options.home_title)
        else:
            isAdmin = self.isAdmin()
            label_list = Label.group(self.db)
            blog_hostname = options.blog_hostname
            self.render('article.html', article=article, label_list=label_list,
                    blog_hostname=blog_hostname, isAdmin=isAdmin, home_title=options.home_title,
                    user=options.user, photo=options.photo)


class PreviewHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        title = self.get_argument('title')
        content_md = self.get_argument('content')
        pattern = r'\[[^\[\]]+\]'
        labels = re.findall(pattern, self.get_argument('labels'))
        content_html = markdown.markdown(content_md, ['codehilite'])

        article = {}
        article['title'] = title
        article['content_html'] = content_html
        article['labels'] = [{'detail': label[1:-1].strip()} for label in labels]

        data = {}
        data['title'] = title
        data['labels'] = self.get_argument('labels')
        data['content'] = content_md

        self.render('preview.html', article=article, data=data,
                user=options.user, photo=options.photo)


class EditArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        article = Article.get(self.db, id)
        if article is None:
            error = '404: Page Not Found'
            self.render('error.html', error=error, home_title=options.home_title)
        else:
            labels = ' '.join(map(lambda item: '[' + item['detail'] + ']', article['labels']))
            self.render('editArticle.html', article=article, labels=labels)


class UpdateArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, id):
        title = self.get_argument('title')
        content_md = self.get_argument('content')
        pattern = r'\[[^\[\]]+\]'
        labels = re.findall(pattern, self.get_argument('labels'))
        content_html = markdown.markdown(content_md, ['codehilite'])

        try:
            Article.update(self.db, id, title, content_md, content_html)
            Label.deleteAll(self.db, id)
            for label in labels:
                detail = label[1:-1].strip()
                Label.create(self.db, id, detail)

            self.redirect('/article/' + id, permanent=True)
        except:
            error = "The post data invalid"
            self.render('error.html', error=error, home_title=options.home_title)


class CreateArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('createArticle.html')

    @tornado.web.authenticated
    def post(self):
        title = self.get_argument('title')
        content_md = self.get_argument('content')
        pattern = r'\[[^\[\]]+\]'
        labels = re.findall(pattern, self.get_argument('labels'))
        content_html = markdown.markdown(content_md, ['codehilite'])

        try:
            article_id = Article.create(self.db, title, content_md, content_html)
            for label in labels:
                detail = label[1:-1].strip()
                Label.create(self.db, article_id, detail)

            self.redirect('/', permanent=True)
        except:
            error = "The post data invalid"
            self.render('error.html', error=error, home_title=options.home_title)


class SearchHandler(BaseHandler):
    def get(self):
        key = self.get_argument('key', '').strip()
        pageId = int(self.get_argument('page', '1'))
        if len(key) == 0:
            results = Article.all(self.db)
        else:
            results = Search.all(self.db, key)
        p = Paginator(results, 5)
        page = p.page(pageId)
        isAdmin = self.isAdmin()
        label_list = Label.group(self.db)

        self.render('search.html', articles=page.object_list, label_list=label_list,
                isAdmin=isAdmin, page=page, home_title=options.home_title,
                user=options.user, photo=options.photo)


class LoginHandler(BaseHandler):
    def get(self):
        next = self.get_argument('next', '/')
        self.render('login.html', next=next)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect('/', permanent=True)


class AuthHandler(BaseHandler):
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        try:
            if self.validate(username) is None:
                raise

            if Auth.authenticate(self.db, username, password):
                self.set_secure_cookie("user", "admin", expires_days=1)
                self.redirect(self.get_argument('next', '/'), permanent=True)
            else:
                self.redirect('/login', permanent=True)
        except:
            error = "The user not exists"
            self.render('error.html', error=error, home_title=options.home_title)

    def validate(self, username):
        regex = re.compile(r'^[\w\d]+$')
        return regex.match(username)


def main():
    config = ConfigParser.ConfigParser()
    config.read('blog.cfg')
    mysql = dict(config.items('mysql'))
    blog = dict(config.items('blog'))

    define("port", default=int(blog['port']), type=int)
    define("mysql_host", default="127.0.0.1:3306")
    define("mysql_database", default=mysql['database'])
    define("mysql_user", default=mysql['user'])
    define("mysql_password", default=mysql['password'])
    define("blog_hostname", default=blog['hostname'])
    define("user", default=blog['user'])
    define("home_title", default=blog['home_title'])
    define("photo", default=blog['photo'])

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
