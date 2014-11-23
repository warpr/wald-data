
wald-storage
============

Implement a basic versioned triple store using:

https://github.com/RDFLib/rdflib-sqlalchemy

Getting Started
---------------

wald-storage defaults to using postgresql as a datastore, and this documentation assumes that
will be your setup.  It should work with any database supported by RDFLib-SQLAlchemy, but that is
untested.

1. Install postgresql and python if you don't have those installed yet, on Ubuntu run this:
```
sudo apt-get install postgresql postgresql-client postgresql-doc postgresql-server-dev-all
sudo apt-get install python-virtualenv python-pip python
```

2. Now run the bootstrap script to install any other required python dependencies:
```
bin/bootstrap
```

3. [create a database](http://www.postgresql.org/docs/9.3/static/app-createdb.html) and if
   necessary a [database user](http://www.postgresql.org/docs/9.3/static/client-authentication.html)
   with sufficient permissions to connect to the database and create tables in the database.

4. Determine the connection string to use based on the previous step, this should look something
   like:
```
postgresql+psycopg2://user:password@hostname:port/database
```
   Edit etc/config.ini and enter your connection URL.

5. Initialize the database:
```
bin/init
```

6. All done, start the service!
```
bin/service
```


License
=======

Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>

This program is free software: you can redistribute it and/or modify
it under the terms of copyleft-next 0.3.0.  See [LICENSE.txt](LICENSE.txt).

