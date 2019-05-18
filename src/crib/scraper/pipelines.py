# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from crib import injection
from crib.scraper import base


class CribPipeline(base.WithInjection):
    property_repository = injection.Dependency()

    def process_item(self, item, spider):
        if item["existing"]:
            self.property_repository.update(item["prop"])
        else:
            self.property_repository.insert(item["prop"])
