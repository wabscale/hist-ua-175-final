#!/usr/bin/env python3

import pyarrow.parquet as pq
import sys

print(sys.argv[1])
df = pq.read_table(open(sys.argv[1], 'rb'))
df.to_pandas().to_csv(sys.argv[1] + '.csv')

