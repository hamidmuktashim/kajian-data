#!/usr/bin/env python3
"""Cetak 2 slug wilayah untuk hari ini (bergilir, 12 wilayah → siklus 6 hari)."""
import datetime, sys
WILAYAH = ["bandung-kota","jaksel","jaktim-jakbar","bogor","tangerang","surabaya",
           "bandung-kab","jakpus-jakut","depok","bekasi","yogyakarta","makassar"]
PER_HARI = 2
n = len(WILAYAH); d = datetime.date.today().toordinal()
mulai = (d * PER_HARI) % n
print(" ".join(WILAYAH[(mulai + i) % n] for i in range(PER_HARI)))
