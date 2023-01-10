from __future__ import annotations

import time

tOld = 0

def reset():
    global tOld
    tOld = time.time()

def lap():
    global tOld
    tnew = time.time()
    t = round(tnew - tOld, 3)
    tOld = tnew
    print(f"The last operation took {t} senconds")
