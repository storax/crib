# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy  # type: ignore


class PropertyItem(scrapy.Item):
    prop = scrapy.Field()
