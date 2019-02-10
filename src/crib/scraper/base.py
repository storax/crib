"""
Common base classes
"""
from crib import injection


class WithInjection(injection.Component):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        from_crawler = getattr(super(WithInjection, cls), "from_crawler", None)
        if from_crawler:
            instance = from_crawler(
                crawler, cls.__name__, crawler.settings["CONTAINER"], *args, **kwargs
            )
        else:
            instance = cls(cls.__name__, crawler.settings["CONTAINER"], *args, **kwargs)
        return instance
