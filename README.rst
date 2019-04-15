crib
====

Crib is supposed to help me find a new place to rent by scraping property data
from websites like rightmove, zoopla etc and provide more advanced filters, and
functionality for finding the right crib. It is very opinionated and only meant
for my personal use.

Crib consists of 3 components:
- a scraper, which collects data and stores it in a database
- a server, that can serve that data back but with advanced filters
- a `web UI <https://github.com/storax/crib-web-ui>`_

Requirements
------------

- Python 3.7
- MongoDB

Installation
------------

The project only comes as source. Install it with your favorite python package
manager.

Usage
-----

MongoDB
+++++++

First set up a mongodb database. Here is an example ``mongod.yaml``
configuration::

  processManagement:
     fork: true
     pidFilePath: /tmp/mongodb.pid
  net:
     bindIp: localhost
     port: 27017
  storage:
     dbPath: /path/to/crib/db/
     journal:
        enabled: true
  systemLog:
     destination: file
     path: /path/to/log/file.log
     logAppend: true

Start mongodb::

  mongod --config mongod.yaml

Crib uses ``localhost:2717`` as default. The settings can be overridden in the config for crib::

  property_repository:
    connection:
      host: 'localhost:27017'
    database: "crib"
  
  user_repository:
    connection:
      host: 'localhost:27017'
    database: "crib"

Scraping
++++++++

The scraper can be configured to scrape properties from rightmove search urls.
Here is an example ``config.yaml``::

  scrape:
    RIGHTMOVE_SEARCHES:
      - "https://www.rightmove.co.uk/property-to-rent/find.html?searchType=RENT&locationIdentifier=REGION%5E1498&insId=1&radius=0.0&minPrice=&maxPrice=&minBedrooms=&maxBedrooms=&displayPropertyType=&maxDaysSinceAdded=&sortByPriceDescending=&_includeLetAgreed=on&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&letType=&letFurnishType=&houseFlatShare="

Crib provides a ``crib`` CLI. You can scrape properties via::

  crib -c config.yaml scrape crawl rightmove

Crib comes with a default configuration for scrapy. You can override them in the
scrape section of the config. See the `scrapy documentation
<https://docs.scrapy.org/en/latest/topics/settings.html>`_ for available
settings.

List availabile spiders with::

  crib -c config.yaml scrape list

Google Directions Service
+++++++++++++++++++++++++

Crib can fetch the time it takes to your work to get commute times. You need an
`API KEY
<https://developers.google.com/maps/documentation/directions/get-api-key>`_ and
set it in the ``config.yaml``. You can also specify your place of work::

  directions_service:
    api-key: CHANGEME
    work-location:
      latitude: 51.0
      longitude: 0.0

Setup user
++++++++++

No idea why you would need users in a personal project designed for a single
person, but I had fun trying to write a login page for the first time in my
life. So you need to register a user::

You might wanna override the default secrets for the srever. The server is a
simple flask application and settings can be specified in the ``server`` of the
config::

  server:
    JWT_SECRET_KEY: .......
    SECRET_KEY: ...

Next register a user via the CLI::

  crib -c config.yaml server add-user test

Start the backend
+++++++++++++++++

::

   crib -c config.yaml server run
