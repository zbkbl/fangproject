# coding:utf-8
from scrapy import signals
import MySQLdb
import MySQLdb.cursors
from scrapy.exceptions import IgnoreRequest

class FangprojectSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    def __init__(self):
        self.conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='3385458', db='fang_test')
        self.cursor = self.conn.cursor()
        self.result = self._conditional_query(self.cursor)

    def _conditional_query(self, tb):
        print u"该函数被执行…………………………………………………………………………………………………………………………"
        url_set = set()
        try:
            tb.execute("select url from t_web_fang_xiaoqu;")
            rs = tb.fetchall()
            for line in rs:
                url_set.add(line[0])
        except Exception, e:
            print e
        return url_set

    def process_request(self, request, spider):
        if request.url not in self.result:
            return None
        else:
            raise IgnoreRequest

