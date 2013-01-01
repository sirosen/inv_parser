===== COPYRIGHT =====

Copyright (c) 2012, Stephen Rosen

===== LICENSING =====

This program is free software: you can
redistribute it and/or modify it under the terms
of the GNU Lesser General Public License as
published by the Free Software Foundation. See
the GNU Lesser General Public License for more
details.

===== WARRANTY =====

This software is distributed without any explicit
or implied warranty of any kind.


===== README =====

The config file is in a specialized format which
does not contain much descriptive information about
the system. Do not look there for comprehensive
explanations.

-----
What is inv-parser?
-----

inv-parser is a python based system for handling
System Profiler reports from OSX.
This is a toolkit which may be useful for
automating polling of hardware status over a large
number of nearly-uniform macs, without using an
ARD database. It was originally developed for use
in a university computer lab, in which it was
desirable to be able to use command line tools to
enter the hardware of each machine into a MySQL
database. It is hoped that this simple piece of
code will prove useful for others.


Apple's System Profiler utility provides a great
deal of hardware and software information readily
without our needing to install any third-party
software. However, it is stored in a particularly
arcane plist file, whose format reportedly changes
with some regularity. This is somewhat
problematic, but we have found that the raw text
output is much more stable.
We parse the raw text output of system profiler
into an element tree, then lookup xpath
expressions on the tree.


-----
Usage
-----

The only script you need to touch is db_insert.py
This makes use of the other modules in the system,
and parses the config file into mappings from
xpath expressions to database insertions.
In order to view the explanation of options, just
run "python db_insert.py -h"

This tool will parse the given report and insert
values into the database directly.
The machine name that you provide must be correct,
otherwise we will fail silently by inserting the
report with the wrong machine name.
Writing the config file should feel fairly
natural, although you should feel free to speak
with the project developer(s) about any changes,
if you are uncertain. Most of it looks like xpath
expressions, although a few extra characters are
supported for convenience.


-----
Components
-----

==profiler.py==
The Profiler module handles parsing of system
profiler output, turning it into an element tree,
a recursive dictionary structure. It allows us to
perform lookups on the report using xpath
expressions, and supports dumping the element
tree to a string of xml.

==locations.py==
Locations is the centralized listing of machine
locations in the lab. It support some simple
lookup operations. We chose not to parse a config
file in order to help simplify the ssh_run system.

==xml_cleanup.py==
The xml_cleanup module is the saddest part of
handling system profiler output. Because Apple
drops a lot of unicode and non-xml compliant
characters, like angle braces, into the system
profiler, we need to clean up these names when
we build our element tree. However, it is often
most convenient to use these uncleaned names in
the config.

==db_insert.py==
db_insert is, unlike the other python modules, a
script. It takes in a config file, a system
profiler report, and a machine name, and performs
an insertion into a MySQL database using the
other modules. In the future, db_insert will not
contain raw values about the database, but will
pull that information from the config file or
another source.
