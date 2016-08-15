
wald:meta
=========

A wald:meta site is a community-editable metadata database.  It is intended to
be used with a community of people to build a living dataset about a particular
topic.

For example it could be used to build a music database like musicbrainz or discogs.

A wald:meta site always has a main dataset (or graph) and a few auxiliary graphs.  If
your wald:meta site is hosted on https://example.com and your main dataset concerns
music, you would have these graphs:

    - https://example.com/music/dataset
    - https://example.com/music/edits
    - https://example.com/meta/dataset
    - https://example.com/meta/edits

Of these, https://example.com/music/dataset is the main dataset you are building.
https://example.com/music/edits is the dataset containing a record of all changes to
the main dataset.

https://example.com/music/edits will grow to be much larger than your actual dataset,
but is not typically useful for most users of your dataset.  wald:meta will in the
future have tools to archive this data to static files, so that it is available to
your visitors if they need it, but doesn't bloat your live databases.

https://example.com/meta/dataset is the metadata dataset, this dataset is used to
run the site itself.  The metadata dataset contains users and their settings, site
pages, etc..

https://example.com/meta/edits is the record of changes to the metadata dataset.
Because the metadata dataset may contain sensitive information about users, this
record of changes is pruned -- in the default cofiguration edits older than two
weeks are wiped from the dataset (FIXME: none of this implemented yet).

Currently a dataset and the record of changes for that dataset are stored as separate
graphs in a single Fuseki dataset.  A wald:site thus has two Fuseki datasets, one
for the main topic of the database and the metadata which runs the site itself.

FIXME: if the above graphs are at the root, that means some paths cannot be used
as dataset names, as they are needed for wald:meta itself.  e.g. /vocab, /colophon,
(any entity pages, for music e.g. /artist, /song, etc..), /user.  Hm, perhaps any
pages needed for the site itself can be entity pages within the metadata dataset.


