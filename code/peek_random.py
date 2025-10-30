# -*- coding: utf-8 -*-
import csv, os
p = os.path.join(os.path.dirname(__file__), 'result.csv')
with open(p, 'r', encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
print('Total:', len(rows))
for idx in [0, len(rows)//2, len(rows)-1]:
    row = rows[idx]
    print(idx+1, {k: row.get(k) for k in ['id','problem','school','username','realname','status','submit_time']})
