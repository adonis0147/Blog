#!/usr/bin/env python
#-*- coding:utf-8 -*-
import hashlib


class Article(object):
    @classmethod
    def all(cls, db):
        articles = db.query('SELECT * FROM article ORDER BY time DESC')
        for article in articles:
            article['labels'] = Label.all(db, article.id)
        return articles

    @classmethod
    def get(cls, db, id):
        article = db.get('SELECT * FROM article WHERE id = %s', id)
        if article is None:
            return article
        else:
            article['labels'] = Label.all(db, article.id)
            return article

    @classmethod
    def create(cls, db, title, content_md, content_html):
        return db.execute('INSERT INTO article (title, content_md, content_html, time) \
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP())', title, content_md, content_html)

    @classmethod
    def update(cls, db, id, title, content_md, content_html):
        db.execute('UPDATE article set title=%s, content_md=%s, \
                content_html=%s WHERE id=%s', title, content_md, content_html, id)

    @classmethod
    def totalNumber(cls, db):
        return db.execute_rowcount('SELECT * FROM article')


class Label(object):
    @classmethod
    def all(cls, db, article_id):
        return db.query('SELECT detail FROM label \
                WHERE article_id = %s', article_id)

    @classmethod
    def create(cls, db, article_id, detail):
        db.execute('INSERT INTO label (article_id, detail) \
                VALUES (%s, %s)', article_id, detail)

    @classmethod
    def deleteAll(cls, db, article_id):
        db.execute('DELETE FROM label WHERE article_id=%s', article_id)

    @classmethod
    def group(cls, db):
        return db.query('SELECT detail, count(*) AS number \
                FROM label GROUP BY detail ORDER BY number DESC')


class Auth(object):
    @classmethod
    def authenticate(cls, db, username, password):
        hashPassword = db.get('SELECT password FROM auth \
                WHERE username = %s', username)['password']
        return hashlib.md5(password).hexdigest() == hashPassword


class Search(object):
    @classmethod
    def all(cls, db, key):
        results = db.query('SELECT a.id, a.title, a.content_md, a.content_html, a.time \
                FROM article a, label l \
                WHERE a.id = l.article_id AND l.detail = %s \
                ORDER BY time DESC', key)
        for result in results:
            result['labels'] = Label.all(db, result.id)
        return results
