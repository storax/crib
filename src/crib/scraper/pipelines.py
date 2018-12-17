# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from crib.scraper import base


class CribPipeline(base.WithRepo):
    def process_item(self, item, spider):
        self.repo.insert(item["prop"])
