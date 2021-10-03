Latin scansion engine
=====================

This library uses finite-state grammars to automate Latin scansion, with an
initial focus on the dactylic hexameters of Virgil.

License
-------

The engine is released under an Apache 2.0 license. Please see
[LICENSE.txt](LICENSE.txt) for details.

Installation
------------

[Conda](http://conda.io) is recommended for a reproducible environment. Assuming
that Conda (either Miniconda or Anaconda) is available, the following command
creates the environment `scansion`.

``` {.bash}
conda env create -f environment.yml
```

This only needs to be done once. The following command then activates the
environment.

``` {.bash}
conda activate scansion
```

This second step needs to be repeated each time you start a new shell.

Installation
------------

1.  Compile the grammar assets:

``` {.bash}
make -j -C grammars
```

2.  Generate the textproto library:

``` {.bash}
make -C latin_scansion/lib
```

3.  Install the Python library:

``` {.bash}
python setup.py install
```

Command-line tools
------------------

Installation produces two command-line tools:

-   [`latin_scan`](latin_scansion/cli/scan.py) scans a document, generating a
    human-readable
    [textproto](https://medium.com/@nathantnorth/protocol-buffers-text-format-14e0584f70a5)
    representation of document's scansion. Sample usage:

``` {.bash}
latin_scan --far grammars/all.far --name "Aeneid, book 1" data/Aeneid/Aeneid01.txt data/Aeneid/Aeneid01.textproto
```

-   [`latin_validate`](latin_scansion/cli/validate.py) validates (and
    optionally, canonicalizes) a textproto document scansion. Sample usage:

``` {.bash}
latin_validate data/Aeneid/Aeneid01.textproto
```

Authors
-------

-   [Jillian Chang](jillianchang15@gmail.com)
-   [Kyle Gorman](kgorman@gc.cuny.edu)

