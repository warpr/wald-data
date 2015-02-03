
wald-storage
============

wald-storage is built on various third-party components:

- Fuseki is used as a database
- Redis is used to mint identifiers
- A Linked Data Fragments server is used as a read-only webservice to the database

Follow the instructions below to set things up.


Step 1.  Install and configure all your requirements
----------------------------------------------------

First, make sure the following are installed:

    java, redis, node.js, python, gnu screen

If you're on an older Ubuntu you may have to use the
[chris lea PPA](https://launchpad.net/~chris-lea/+archive/ubuntu/node.js) to install node.js.

The other requirements can be installed with:

    sudo apt-get install openjdk-7-jdk redis-server screen
    sudo apt-get install python-virtualenv python-pip
    bin/bootstrap

The bootstrap script will install various third-party python libraries in a virtualenv.  It will
also download Fuseki and the node.js [Linked Data Fragments](http://linkeddatafragments.org/software/)
server. [Fuseki](https://jena.apache.org/documentation/serving_data/) is the SPARQL server included
in the Apache Jena project.


Step 2.  Configure your wald:meta site
--------------------------------------

Create a new folder for your wald:meta site and copy etc/waldmeta.json to the root of your new
site.  Edit the file, and then run init to configure your site:

    ~/projects/wald-data$ cd ..
    ~/projects$ mkdir my-website
    ~/projects$ cd my-website
    ~/projects/my-website$ cp ../wald-data/etc/waldmeta.json .
    ~/projects/my-website$ vim waldmeta.json
    ~/projects/my-website$ ../wald-data/bin/init

init will generate various configuration files and startup scripts in the bin/ and etc/ folders
of your site.  You can now run bin/start to run your site, this will start both the linked data
fragment server and fuseki.  For a production setup you probably want to have more control of how
these services run, in that case check the start script on how these services are expected to
run.


License
=======

Copyright (C) 2015  Kuno Woudt <kuno@frob.nl>

This program is free software: you can redistribute it and/or modify
it under the terms of copyleft-next 0.3.0.  See [LICENSE.txt](LICENSE.txt).

