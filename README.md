
wald-storage
============

Implement a basic versioned triple store using:

https://github.com/RDFLib/rdflib-sqlalchemy

Getting Started
---------------

wald-storage defaults to using postgresql as a datastore, and this documentation assumes that
will be your setup.  It should work with any database supported by RDFLib-SQLAlchemy, but that is
untested.

Currently SQLAlchemy is also used to atomically mint sequential identifiers.


Step 1.  Install and configure all your requirements
----------------------------------------------------

Install postgresql and python if you don't have those installed yet, on Ubuntu run this:

    sudo apt-get install postgresql postgresql-client postgresql-doc postgresql-server-dev-all
    sudo apt-get install python-virtualenv python-pip python

Now run the bootstrap script to install any other required python dependencies:

    bin/bootstrap

[Create a database](http://www.postgresql.org/docs/9.3/static/app-createdb.html) and if necessary
a [database user](http://www.postgresql.org/docs/9.3/static/client-authentication.html) with
sufficient permissions to connect to the database and create tables in the database.

Determine the connection string to use, this should look something like:

    postgresql+psycopg2://user:password@hostname:port/database

Edit etc/config.ini and enter your connection string.


Step 2. Creating your dataset
-----------------------------

To initialize the database you will have to decide on the name of the dataset for your
project. In the future wald:meta will support multiple datasets in one deployment, but currently
only one is supported.  The dataset name will be used as an identifier in various places, so
should a simple lowercase ascii string without special characters, i.e. it should match this
regex: /^[a-zA-Z][a-zA-Z0-9.-]*$/.  wald:meta will always create a "meta" dataset for your
wald:meta install which will contain user accounts and permissions.

You also need a base url to indicate at what location your project will be made available, the
base url will be used to mint various identifiers.  For example, if you have a dataset called
"books" and https://example.com/library as a base url, the following API roots will be available:

- https://example.com/library/books/dataset (Your book database)
- https://example.com/library/books/edits (History of changes made to your book database)
- https://example.com/library/meta/dataset (Metadata necessary to interact with your book database)
- https://example.com/library/meta/edits (History of changes made to the metadata)

To initialize your dataset run bin/init:

    bin/init <base url> <dataset>

All done, start the service!

    bin/service

NOTE: if you want to use multiple datasets, specify them as a comma separated list, e.g.:

    bin/init https://example.com/library books,music,movies


License
=======

Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>

This program is free software: you can redistribute it and/or modify
it under the terms of copyleft-next 0.3.0.  See [LICENSE.txt](LICENSE.txt).

