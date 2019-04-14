"""
Common base classes
"""
from functools import partial

from crib import injection


class WithInjection(injection.Component):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        from_crawler = getattr(super(WithInjection, cls), "from_crawler", None)
        factory = partial(from_crawler, crawler) if from_crawler else cls

        instance = factory(cls.__name__, crawler.settings["CONTAINER"], *args, **kwargs)
        return instance
