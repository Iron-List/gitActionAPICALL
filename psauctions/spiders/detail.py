# -*- coding: utf-8 -*-
import scrapy,re
import logging
import requests
from Almarwan.items import AlmarwandetailItem
from scrapinghub import ScrapinghubClient


class DetailSpider(scrapy.Spider):
    name = 'detail'
    allowed_domains = ['almarwanequipment.com']
    start_urls = ['https://almarwanequipment.com/']
    project_id = 537942
    # custom_settings = {
    #     'CLOSESPIDER_TIMEOUT': 7200
    # }

    def __init__(self, collection_name=None, *args, **kwargs):
        super(DetailSpider, self).__init__(*args, **kwargs)
        global current_collection, url, serial_number, year_list, vendor_phone, img_url, listing_urls, category_names, thumb_urls, collection_keys, foo_store, title, city, price_list, subCategory_names, country , machine_type , currency , maincategory, location, make, model
        listing_urls = []
        maincategory = []
        category_names = []
        collection_keys = []
        thumb_urls = []
        title = []
        city = []
        currency = []
        country = []
        price_list = []
        img_url = []
        location = []
        vendor_phone = []
        serial_number = []
        year_list = []
        make = []
        model = []

        machine_type = []
        subCategory_names = []
        current_collection = ''

        logging.basicConfig()
        logger = logging.getLogger('logger')
        apikey = 'a77f8d9112a14cd6bfc4e3734261b2aa'
        client = ScrapinghubClient(apikey)
        project = client.get_project(self.project_id)
        collections = project.collections
        if not collection_name:
            collection_list = collections.list()[-1]
            collection_name = collection_list.get('name')
            foo_store = collections.get_store(collection_name)
            print("MyStore", collection_name)
        else:
            foo_store = collections.get_store(collection_name)
        current_collection = str(collection_name)
        print("Getting Items from collection" + str(collection_name))
        print("Length of collection" + str(foo_store.count()))

        for elem in foo_store.iter():
            collection_keys.append(elem['_key'])
            listing_urls.append(elem['item_url'])
            maincategory.append(str(elem['category'].get('cat1_name')))
            category_names.append(str(elem['category'].get('cat2_name')))
            thumb_urls.append(str(elem['thumbnail_url']))
            title.append(str(elem['title']))
            year_list.append(elem['item_custom_info'].get('year'))

        print("Fetched from collection" + str(collection_name))

    def parse(self, response):
        for i in range(len(listing_urls)):
            title_ = title[i]
            thumb_urls_ = thumb_urls[i]
            year = year_list[i]
            cat1_name = maincategory[i]
            url = listing_urls[i]
            collection_item_keys = collection_keys[i]
            yield scrapy.Request(url,self.parse_data,meta={'title':title_,'year':year,
                                                           'thumb_urls':thumb_urls_,
                                                           'cat1_name':cat1_name,
                                                           'collection_item_key':collection_item_keys})

    def parse_data(self,response):
        item = AlmarwandetailItem()

        item['model'] = response.xpath(
            "//ul[@class='iconlist']/li/.//*[contains(text(),'Model:')]/following-sibling::text()").get('').strip()
        item['make'] = response.xpath(
            "//ul[@class='iconlist']/li/.//*[contains(text(),'Brand:')]/following-sibling::a/strong/text()").get(
            '').strip()
        if str(item['make']) in str(item['model']):
            item['model'] = item['model'].replace(item['make'],'').strip()
        if "Others" in item['make']:
            item['make'] = ""
        if not item['make']:
            item['model'] = ''
        item['item_url'] = response.url
        item['item_title'] = response.xpath("//div[@class='container clearfix']/h1/text()").get('') or ''

        item['item_main_category'] = response.meta.get('cat1_name') or ''
        item['item_main_category_id'] = response.meta.get('cat1_name') or ''

        cat2_name = response.xpath("//ul[@class='iconlist']/li/.//*[contains(text(),'Group:')]/following-sibling::a/text()").get('').strip()
        if cat2_name:
            item['item_source_sub_category_id'] = cat2_name
            item['item_sub_category'] = cat2_name
            item['item_category'] = cat2_name
            item['item_source_category_id'] = cat2_name
        else:
            item['item_source_sub_category_id'] = response.meta.get('category1') or ''
            item['item_sub_category'] = response.meta.get('category1') or ''
            item['item_category'] = response.meta.get('category1') or ''
            item['item_source_category_id'] = response.meta.get('category1') or ''

        item['buying_format'] = 'sale'


        year = response.meta.get('year') or ''
        try:
            year = int(year)
            if 1900 <= year <= 2021:
                item['year'] = year
            else:
                item['year'] = ''
        except:
            item['year'] = ''

        try:
            hour = ''
            hour = int(re.sub('\D', '', hour))
        except:
            hour = ''

        item['extra_fields'] = {
            'hours': ''
        }

        item['location'] = item['vendor_location'] = "Industrial Area 15, Sharjah, United Arab Emirates"


        item['price_original'] = ''
        item['price'] = ''

        price = response.xpath("//div[@class='first group_1of3']/span/text()").get('')
        if price != '':
            try:
                price = re.sub('\D', '', price)
                price = int(price)
                item['price_original'] = item['price'] = price
                item['currency'] = "USD"
            except:
                item['price_original'] = item['price'] = ''
                item['currency'] = ''

        img_url = response.xpath("//div[@class='slide']/a/@href").getall()
        img_url = ["https://almarwanequipment.com" + i for i in img_url]
        item['img_url'] = img_url
        item['thumbnail_url'] = response.meta['thumb_urls'].strip('null')
        if item['thumbnail_url'] == '':
            if len(img_url) >= 1:
                item['thumbnail_url'] = img_url[0]
            else:
                item['thumbnail_url'] = ''
                item['thumbnail_s3_path'] = '/thumbnailimagenotfound.jpg'

        # if 'http' not in item['thumbnail_url']:
        #     item['thumbnail_url'] = ''
        #     item['thumbnail_s3_path'] = '/thumbnailimagenotfound.jpg'

        item['vendor_name'] = 'AL Marwan'

        item['source_item_id'] = 'ironlist' + str(537942) + response.meta['collection_item_key']
        yield item


