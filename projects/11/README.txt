compiler.py by Santiago Larrain
-------------------------------
compiler.py is a python program that executes project 11

How to run
----------
The code is written in python3 and it uses the following packages:
[They should all be installed by default]
re
sys
itertools
xml.etree.ElementTree
xml.dom
import glob

It relies on the following classes / files, that are on the same 'src' folder:
tokenizer.py      [From project 10 with small modifications]
symbolTable.py    [New to project 11 - Creates the symbol Table]
compilator.py     [New to project 11 - The engine. Does the heavy lifting]
VMWriter.py       [New to project 11 - Simple writer following the API]

Usage
-----
The program creates *.vm files from *.jack files with the same name. You can
also pass a folder and will convert every *.jack file to a *.vm file

$ python3 compiler.py inputfile.jack
or
$ python3 compiler.py ../path/to/folder/

This programs has not been tested outside a Unix enviroment.
