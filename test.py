#import sys
#import os

#sys.path.append(os.getcwd())   # adds current folder to path

from Parser.nastran_parser import parse_f06

data = parse_f06("sample.f06")
print(data)