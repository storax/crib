"""
Common base classes
"""
from crib import app


class WithConfig(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = {}

    @classmethod
    def from_crawler(cls, crawler):
        from_crawler = getattr(super(WithConfig, cls), "from_crawler", None)
        instance = from_crawler(crawler) if from_crawler else cls()
        instance.config = crawler.settings.getdict("CRIB")
        return instance


class WithRepo(WithConfig):
    @classmethod
    def from_crawler(cls, crawler):
        instance = super(WithRepo, cls).from_crawler(crawler)
        instance.repo = app.get_property_repository(instance.config)
        return instance
