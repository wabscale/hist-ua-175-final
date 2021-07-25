#!/usr/bin/env python3

import pyarrow.feather as feather
import sys

df = feather.read_feather(sys.argv[1])
df.to_csv(sys.argv[1] + '.csv')

