import pluggy

hookspec = pluggy.HookspecMarker("crib")


@hookspec
def crib_add_scrapers():
    """Add scraper plugins

    :return: a list of scrapers
    """
