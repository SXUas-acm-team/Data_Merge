# -*- coding: utf-8 -*-
import csv, os
p = os.path.join(os.path.dirname(__file__), 'oj_sub.csv')
if not os.path.exists(p) or os.path.getsize(p) == 0:
    print('EMPTY')
else:
    with open(p, 'r', encoding='utf-8-sig', newline='') as f:
        r = csv.reader(f)
        try:
            header = next(r)
        except StopIteration:
            print('EMPTY')
        else:
            print('HEADER:', header)
            for i, row in enumerate(r, 1):
                print('ROW:', row)
                if i >= 3:
                    break
