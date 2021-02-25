import logging

from crib import exceptions, injection, plugins

log = logging.getLogger(__name__)


class ScapeService(plugins.Plugin):
    _scrape = injection.Dependency("scrape")

    def scrape(self, search):
        spider = "rightmove"
        settings = {
            "RIGHTMOVE_SEARCHES": [search],
        }
        self._scrape.crawl(spider, loglevel="INFO", settings=settings)
