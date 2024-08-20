# Superblame

### About
Superblame is a simple recommendation system used to find a suitable reviewer for
your patch.

### Version Control Support
* Git
* Mercurial

### Requirements
* Python 3.x

### Installation
`superblame.py` is a stand-alone Python script and does not require
installation. The install procedure just creates the symbolic link `superblame`
in a common directory in your path (currently set to `/usr/bin`).
If that's what you want, just use

    make install

### Usage
First, navigate to the repository root, or use `--src` to set it accordingly.

#### Case 1: You want to find a reviewer for your current changeset
Simply use

    superblame

#### Case 2: You want to find a reviewer for an existing patch
Just provide the path to the patch

    superblame <patch>

#### Output
The output is a ranked list of editors. The relevance of an editor to your
changeset is given my the number of `#`. Let's look at the following output

      Peter #######################
    Grigory ##############
        Eve ###########
       Hans ####
      Joshi ##
    Randall #

It tells us, that `Peter` is the most suitable reviewer for the changeset, with
`Grigory` and `Eve` being good alternatives.

Use `--help` for more details.

### License
The MIT License.
