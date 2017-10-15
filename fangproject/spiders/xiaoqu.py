# -*- coding: utf-8 -*-

import scrapy
from fangproject.items import FangprojectItem
import re
import time
from datetime import datetime, date, timedelta
import sys
reload(sys)
sys.setdefaultencoding('utf8')

city_dict = {
    u'北京': 1, u'上海': 2, u'厦门': 3, u'南京': 4, u'成都': 5, u'青岛': 6,
    u'武汉': 7, u'济南': 8, u'石家庄': 9, u'郑州': 10, u'合肥': 11, u'西安':12
}



class XiaoquSpider(scrapy.Spider):
    name = "xiaoqu"
    # allowed_domain = ['http://esf.fang.com/']
    start_urls = {
        # 'http://esf.fang.com/housing/',
        # 'http://esf.sh.fang.com/housing/',
        # 'http://esf.xm.fang.com/housing/',
        # 'http://esf.nanjing.fang.com/housing/',
        # 'http://esf.cd.fang.com/housing/',
        # 'http://esf.qd.fang.com/housing/',
        # 'http://esf.wuhan.fang.com/housing/',
        # 'http://esf.jn.fang.com/housing/',
        # 'http://esf.sjz.fang.com/housing/',
        # 'http://esf.zz.fang.com/housing/',
        # 'http://esf.hf.fang.com/housing/',
        'http://esf.xian.fang.com/housing/',
    }

    # 获取区域连接
    def parse(self, response):
        u = response.url
        URL = u.split(r"/housing/")[0]
        nurls = response.xpath("//div[@style='z-index: 2']//a/@href").extract()
        urls = nurls[1:]
        for url in urls:
            new_url = URL + url
            # print new_url
            yield scrapy.Request(url=new_url, callback=self.parse_stock)

    # 选取商圈
    def parse_stock(self, response):
        url_s = response.xpath("//p[@id='shangQuancontain']//a/@href").extract()
        urls = url_s[1:]
        u = response.url
        URL = u.split(r"/housing/")[0]
        for url in urls:
            new_url = URL + url
            yield scrapy.Request(url=new_url, callback=self.parse_zhuzhai)

    # 获取住宅类型
    def parse_zhuzhai(self, response):
        url_s = response.xpath("//li[@id='houselist_B03_03']//a/@href").extract()
        urls = url_s[1:3]
        u = response.url
        URL = u.split(r"/housing/")[0]
        for url in urls:
            new_url = URL + url
            yield scrapy.Request(url=new_url, callback=self.parse_url)

    # 获取小区列表
    def parse_url(self, response):
        select = scrapy.Selector(response)
        u = response.url
        URL = u.split(r"/housing/")[0]
        urls = select.xpath("//div[@class='houseList']/div[@class='list rel']")
        for url in urls:
            n_url = url.xpath("./dl/dt/a/@href").extract()[0]
            if 'fang' in n_url:
                yield scrapy.Request(url=n_url, callback=self.parse_item)
                # pass
        next_page = select.xpath("//div[@id='houselist_B14_01']/a[@id='PageControl1_hlk_next']/@href").extract()
        if next_page:
            next_page = URL + next_page[0]
            yield scrapy.Request(next_page, self.parse_url, dont_filter=True)

    def parse_item(self, response):

        select = scrapy.Selector(response)
        html = response.body.decode('gb2312', 'ignore')

        item = FangprojectItem()

        item['url'] = response.url

        # 城市ID
        city_str = select.xpath('//*[@id="dsy_H01_01"]/div[1]/a/text()').extract()
        try:
            for city_key in city_dict.keys():
                if city_key == city_str[0]:
                    city_id = city_dict[city_key]
                    item['city_id'] = city_id
        except Exception, e:
            print e

        # 小区名字
        name = select.xpath("//div[@class='firstright']/div/h1/strong/text()").extract()
        if name:
            item['name'] = name[0]

        # 小区均价
        ave = re.findall(u"小区均价：</strong><em>(.*?)<", html) or re.findall(u'<span class="prib">(.*?)</span>', html)
        # print ave
        if ave:
            item['averagePrice'] = ave[0]
        else:
            item['averagePrice'] = 0

        # 小区均价时间
        ave_time = re.findall(u'>(.*?)月参考价',html)
        if ave_time:
            item['ave_time'] = ave_time[0]

        # 总栋数
        totalBuildings = re.findall(u"楼栋总数：</strong>(.*?)栋</li>", html) or re.findall(u"楼栋总数</strong>(.*?)栋<",html)
        if totalBuildings:
            item['totalBuildings'] = totalBuildings[0]
        else:
            item['totalBuildings'] = 0

        # 物业公司
        property_company = re.findall(u"物业公司：</strong>(.*?)<", html) or re.findall(u"物业公司</strong>(.*?)<", html)
        if property_company:
            item['propertyCompany'] = property_company[0]
        else:
            item['propertyCompany'] = u'暂无资料'

        # 周边学校
        school = re.findall(r'style="color: #333;text-decoration:none;">(.*?)</a>', html)
        if school:
            item['school'] = school[0]
        else:
            item['school'] = u'暂无资料'

        # 学区评级
        xuequ = select.xpath("//div[@class='xqgrade clearfix']/div[@class='s3']/p[last()]/text()").extract()
        if xuequ:
            item['school_district'] = xuequ[0]

        # 详情连接
        url = response.url + '/xiangqing/'
        if url:
            yield scrapy.Request(url=url, meta={'item': item}, callback=self.parse_details)

        # for key, value in item.items():
        #     print key, value

    def parse_details(self, response):
        content = response.body.decode("gbk", 'ignore')
        item = response.meta['item']
        # select = scrapy.Selector(response)

        # 小区位置
        location = re.findall(u"所属区域：</strong>(.*?)<", content)
        if location:
            details = location[0].split(" ")
            item['district'] = details[0]
            item['community'] = details[1]

        # 竣工时间
        buildtime = re.findall(u"竣工时间：</strong>(.*?)<", content)
        # if buildtime and buildtime[0] != '0000-00-00':
        #     build_time = datetime.strptime(buildtime[0], '%Y-%m-%d')
        if buildtime:
            item['buildTime'] = buildtime[0]
        else:
            item['buildTime'] = None
        # else:
        #     item['buildTime'] = datetime.strptime('1970-01-01', '%Y-%m-%d')

        # 总户数
        total_users = re.findall(u"总 户 数：</strong>(.*?)户<", content)
        if total_users:
            item['totalUsers'] = total_users[0]
        else:
            item['totalUsers'] = 0

        # 物业类别
        property_type = re.findall(u"物业类别：</strong>(.*?)<", content)
        if property_type:
            item['propertyType'] = property_type[0]
        else:
            item['propertyType'] = u"暂无资料"

        # 容积率
        accumulation_rate = re.findall(u"容 积 率：</strong>(.*?)<", content)
        if accumulation_rate:
            item['accumulationRate'] = accumulation_rate[0]
        else:
            item['accumulationRate'] = 0

        # 绿化率
        green_rate = re.findall(u"绿 化 率：</strong>(.*?)<", content)
        if green_rate:
            item['greenRate'] = green_rate[0]
        else:
            item['greenRate'] = 0

        # 物业费
        property_fee = re.findall(u"物 业 费：</strong>(.*?)元", content)
        if property_fee:
            item['propertyFee'] = property_fee[0]
        else:
            item['propertyFee'] = 0

        # 开发商
        developers = re.findall(u"开 发 商：</strong>(.*?)<", content)
        if developers:
            item['developers'] = developers[0]
        else:
            item['developers'] = u'暂无资料'

        # 小区地址
        adr = re.findall(u"小区地址：</strong>(.*?)<", content) or re.findall(u"小区位置</strong>(.*?)<", content)
        if adr:
            item['adress'] = adr[0]
        else:
            item['adress'] = u'暂无资料'

        # 停车位
        parking = re.findall(u"停 车 位：</strong>(.*?)</dt>", content)
        if parking:
            item['parking_space'] = parking[0]
        else:
            item['parking_space'] = u'暂无资料'
        # 周边公交
        bus = re.findall(u"公交：(.*?)<", content)
        if bus:
            item['bus'] = bus[0]
        else:
            item['bus'] = u'暂无资料'
        # 周边地铁
        subway = re.findall(u"地铁：(.*?)<", content)
        if subway:
            item['subway'] = subway[0]
        else:
            item['subway'] = u'暂无资料'
        # 周边商场
        market = re.findall(u"商场：(.*?)<", content)
        if market:
            item['market'] = market[0]
        else:
            item['market'] = u'暂无资料'
        # 周边医院
        hospital = re.findall(u"医院：(.*?)<", content)
        if hospital:
            item['hospital'] = hospital[0]
        else:
            item['hospital'] = u'暂无资料'
        # 周边学校
        prog = re.compile(u'<dt>幼儿园：(.*?)</dt>		<dt>中小学：(.*?)</dt>		<dt>大学：(.*?)</dt>')
        school = prog.findall(content)
        if school:
            item['school'] = "".join(school[0])

        item['crawl_time'] = time.strftime('%Y-%m-%d')

        # for key, value in item.items():
        #     print key, value

        yield item
