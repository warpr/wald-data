
wald:data
=========

wald:data is built on various third-party components:

- Fuseki is used as a database
- Redis is used to mint identifiers
- A Linked Data Fragments server is used as a read-only webservice to the database

Follow the instructions below to set things up.


Step 1.  Install and configure all your requirements
----------------------------------------------------

First, make sure the following are installed:

    java, redis, node.js, python, gnu screen

On Fedora 23 (FIXME: check if additional package repos need to be enabled):

    sudo dnf -y install java-1.8.0-openjdk redis screen
    sudo dnf -y install python-virtualenv python-pip nodejs
    bin/bootstrap

The bootstrap script will install various third-party python libraries in a
virtualenv.  It will also download Fuseki and the node.js [Linked Data
Fragments](http://linkeddatafragments.org/software/)
server. [Fuseki](https://jena.apache.org/documentation/serving_data/) is the SPARQL
server included in the Apache Jena project.


License
=======

Copyright 2016  Kuno Woudt <kuno@frob.nl>

This program is free software: you can redistribute it and/or modify
it under the terms of copyleft-next 0.3.1.  See
[copyleft-next-0.3.1.txt](copyleft-next-0.3.1.txt).

