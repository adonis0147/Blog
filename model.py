#!/usr/bin/env python
#-*- coding:utf-8 -*-


class Article(object):
    @classmethod
    def all(cls, db):
        articles = db.query('SELECT * FROM article ORDER BY time DESC')
        for article in articles:
            article['labels'] = Label.all(db, article)
        return articles

    @classmethod
    def get(cls, db, id):
        article = db.query('SELECT * FROM article WHERE id = %s', id)[0]
        article['labels'] = Label.all(db, article)
        return article

    @classmethod
    def create(cls, db, title, content_md, content_html):
        return db.execute('INSERT INTO article (title, content_md, content_html, time) \
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP())', \
                title, content_md, content_html)


class Label(object):
    @classmethod
    def all(cls, db, article):
        return db.query('SELECT detail FROM label \
                WHERE article_id = %s', article.id)

    @classmethod
    def create(cls, db, article_id, detail):
        db.execute('INSERT INTO label (article_id, detail) \
                VALUES (%s, %s)', article_id, detail)
