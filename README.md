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

```bash
conda env create -f environment.yml
```

This only needs to be done once. The following command then activates the
environment.

```bash
conda activate scansion
```

This second step needs to be repeated each time you start a new shell.

Compilation
-----------

Good-ole `make` is used for compiling grammars and other assets. The following
command builds all the necessary assets.

```bash
make -j -C grammars
make -C src
```

Authors
-------

-   [Jillian Chang](jillianchang15@gmail.com)
-   [Kyle Gorman](kgorman@gc.cuny.edu)

