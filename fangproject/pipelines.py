# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
import copy


class FangprojectPipeline(object):

    def __init__(self):
        self.conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='3385458',db='fang_test')
        self.cursor = self.conn.cursor()
        self.result = self._conditional_query(self.cursor)

    def process_item(self, item, spider):
        if item['url'] not in self.result:
            return item
        else:
            raise DropItem("小区 %s 已存在。。。" % item['name'])

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


class MySQLPipeline(object):

    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb', host='127.0.0.1',
                                            db='fang_test', user='root',
                                            passwd='3385458', cursorclass=MySQLdb.cursors.DictCursor,
                                            charset='utf8', use_unicode=True)

    def process_item(self, item, spider):
        asynitem = copy.deepcopy(item)
        self.dbpool.runInteraction(self._conditional_insert, asynitem,spider)

        return item

    def _conditional_insert(self, tb, item,spider):
        try:
            print "************************************************************"
            tb.execute("insert into t_web_fang_xiaoqu (city_id,residence_name,district,community,avg_time,avg_price,total_buildings,total_house,\
                       green_rate,accumulation_rate,developer,property_company,build_time,address,property_price,property_type,school_district,parking_space,\
                       subway,bus,market,school,hospital,url,crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",\
                       (item['city_id'], item['name'],item['district'],item['community'],item['ave_time'],item['averagePrice'],item['totalBuildings'],item['totalUsers'],\
                        item['greenRate'],item['accumulationRate'],item['developers'],item['propertyCompany'],item['buildTime'],item['adress'],item['propertyFee'], \
                        item['propertyType'],item['school_district'],item['parking_space'],item['subway'],item['bus'],item['market'],item['school'],item['hospital'],item['url'],item['crawl_time']))
            spider.logger.info("data insert is successful!!!")
        except Exception,e:
            print e
# if __name__ =="__main__":
#     f = FangprojectPipeline()
