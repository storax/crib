"""
Package for scraping property sites like rightmove.co.uk.
"""
from scrapy.crawler import CrawlerProcess  # type: ignore
from scrapy.settings import Settings  # type: ignore
from scrapy.spiderloader import SpiderLoader  # type: ignore

from crib import injection


class Scraper(injection.Component):
    config = injection.Infrastructure()

    def __init__(self, name, container) -> None:
        super(Scraper, self).__init__(name, container)
        self.settings = Settings()
        self.settings.setdict(self.config)
        self.settings.set("CONTAINER", container)
        self._process = None

    def crawl(self, spider, loglevel, settings_override=None):
        if self._process:
            self.process.stop()
        settings = self.settings.copy()
        if settings_override:
            settings.update(settings_override, priority="cmdline")
        if loglevel:
            settings.set("LOG_ENABLED", True, priority="cmdline")
            settings.set("LOG_LEVEL", loglevel, priority="cmdline")
        self._process = CrawlerProcess(settings)
        self._process.crawl(spider)
        self._process.start()

    def list_spiders(self):
        loader = SpiderLoader.from_settings(self.settings)
        return loader.list()
