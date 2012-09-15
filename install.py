#!/usr/bin/env python
#-*- coding:utf-8 -*-
import ConfigParser
import MySQLdb
import getpass
import hashlib
import re
import subprocess

print('=' * 50)
print('安装脚本'.center(54))
print('=' * 50)

print

config = ConfigParser.ConfigParser()
user = raw_input('请输入连接数据库的用户名: ')
passwd = getpass.getpass('请输入连接数据库的密码: ')

with MySQLdb.connect(user=user, passwd=passwd) as c:
    print('连接成功!')

    print

    while True:
        database = raw_input('请输入需要创建的数据库名: ')
        mysqlUser = raw_input('请输入该博客连接数据库的用户名: ')
        mysqlPassword = getpass.getpass('请输入该博客连接数据库的密码: ')
        confirm = getpass.getpass('请再输入一次: ')
        if confirm == mysqlPassword:
            break
        else:
            print
    c.execute("grant all privileges on %s.* to '%s'@'localhost' identified by '%s'" %
            (database, mysqlUser, mysqlPassword))
    c.execute('create database %s' % database)

    config.add_section('mysql')
    config.set('mysql', 'user', mysqlUser)
    config.set('mysql', 'password', mysqlPassword)
    config.set('mysql', 'database', database)

    subprocess.call("mysql --user=%s --password=%s --database=%s < schema.sql" %
            (mysqlUser, mysqlPassword, database), shell=True)

    print('数据库初始化成功!')

    print

    while True:
        while True:
            adminUsername = raw_input('请输入博客管理员的用户名: ')
            if not re.match(r'^[\w\d]+$', adminUsername):
                print('用户名只能由字母和数字组成')
                print
            else:
                break

        adminPassword = getpass.getpass('请输入博客管理员的密码: ')
        confirm = getpass.getpass('请再输入一次: ')
        if confirm == adminPassword:
            break
        else:
            print
    adminPassword = hashlib.md5(adminPassword).hexdigest()
    c.execute('use %s' % database)
    c.execute("insert into auth (username, password) values ('%s', '%s')" %
            (adminUsername, adminPassword))

    print('管理员用户创建完成!')

    print

    hostname = raw_input('请输入博客域名: ')
    port = raw_input('请输入程序监听的端口号: ')
    user = raw_input('请输入博主的名字（默认: Adonis Ling）: ')
    home_title = raw_input("请输入主页的标题（默认: Adonis's Blog ）: ")
    photo = raw_input('请输入博主头像的文件名(默认: talent.jpg）')

    if len(user) == 0:
        user = 'Adonis Ling'
    if len(home_title) == 0:
        home_title = "Adonis's Blog"
    if len(photo) == 0:
        photo = 'talent.jpg'

    config.add_section('blog')
    config.set('blog', 'hostname', hostname)
    config.set('blog', 'port', port)
    config.set('blog', 'user', user)
    config.set('blog', 'home_title', home_title)
    config.set('blog', 'photo', photo)

    with open('blog.cfg', 'w') as cfg:
        config.write(cfg)

    print('配置文件生成成功!')

    print

    raw_input('Press any key to continue...')
