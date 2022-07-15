# -*- coding: utf-8 -*-
import scrapy,time,json
from Almarwan.items import AlmarwanListingItem
import re





class ListingSpider(scrapy.Spider):
    name = 'listing'
    allowed_domains = ['almarwanequipment.com']
    start_urls = ['https://almarwanequipment.com/']

    count = 0




    def parse(self,response):
        cat1_name = response.xpath("//*[contains(@class,'feature-box fbox-center fbox-bg fbox-light fbox-effect')]/a/h3/text()").getall()
        cat1_url = response.xpath("//*[contains(@class,'feature-box fbox-center fbox-bg fbox-light fbox-effect')]/a/@href").getall()
        for key, val in zip(cat1_name, cat1_url):
            val = "https://almarwanequipment.com"+val
            yield scrapy.Request(val, self.parse_data, meta={'cat1_name': key})

    def parse_data(self,response):
        prod_url = response.xpath("//*[contains(text(),'Read More')]/@href").getall()
        for url in prod_url:
            url = 'https://almarwanequipment.com' + url
            yield scrapy.Request(url, self.parse_data1,meta={'cat1_name': response.meta.get('cat1_name')})

    def parse_data1(self, response):
        item = AlmarwanListingItem()
        data = response.xpath("//*[@class='product clearfix']")
        for i in data:
            if not i.xpath(".//*[contains(@class,'sold')]").get(''):
                item['item_url'] = "https://almarwanequipment.com"+i.xpath(".//*[@class='product-desc']//a/@href").get('')
                item['title'] = i.xpath(".//*[@class='product-desc']//a/h2/text()[1]").get('')
                year = i.xpath(".//*[@class='product-desc']//a/h2/text()[2]").get('')
                try:
                    year = re.sub("\D",'',year)
                    if year:
                        year = int(year)
                except:
                    year = ""
                item['item_custom_info'] = {
                    'year': year
                }
                thumbnail_url = i.xpath("//*[@class='product clearfix']/.//*[@class='product-image']/a/img/@src").get('')
                if thumbnail_url:
                    item['thumbnail_url'] = "https://almarwanequipment.com" + thumbnail_url
                item['category'] = {
                    'cat1_name': response.meta.get('cat1_name') or '',
                    'cat1_id': response.meta.get('cat1_name') or ''
                }
                yield item

            next = response.xpath("//li[@class='next']/a/@href").get('')
            if next:
                next = "https://almarwanequipment.com" + next
                yield scrapy.Request(next, self.parse_data1,meta={'cat1_name':response.meta.get('cat1_name')})