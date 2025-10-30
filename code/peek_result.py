# -*- coding: utf-8 -*-
import csv, os
p = os.path.join(os.path.dirname(__file__), 'result.csv')
with open(p, 'r', encoding='utf-8-sig', newline='') as f:
    r = csv.DictReader(f)
    for i, row in enumerate(r, 1):
        print(i, row)
        if i >= 5:
            break
