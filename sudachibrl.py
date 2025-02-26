#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sudachipy import tokenizer
from sudachipy import dictionary
import braillel_rules_pb2
import sys

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.B

print("Input Japanese sentense and hit enter key!")
for line in sys.stdin:
    line = line.strip()
    list = tokenizer_obj.tokenize(line, mode)
    for m in list:
        print(f"{m.reading_form()} ", end="")
    print("\n")

print("End")