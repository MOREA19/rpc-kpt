"""L3.3 - 50 transfer dari 10 thread client secara bersamaan.
Jalankan server dengan:  --no-lock --slow-prob 0 [--race-delay 0.001]
"""
import uuid
from concurrent.futures import ThreadPoolExecutor

import akademik_pb2 as pb
from klien_util import buat_stub, cetak_saldo

N, JUMLAH, THREAD = 50, 10.0, 10
channel, stub = buat_stub()
awal = stub.GetSaldo(pb.SaldoRequest())


def kirim(_):
    return stub.Transfer(pb.TransferRequest(request_id=str(uuid.uuid4()),
                                            dari="A", ke="B", jumlah=JUMLAH), timeout=10)


with ThreadPoolExecutor(max_workers=THREAD) as ex:
    list(ex.map(kirim, range(N)))

s = cetak_saldo(stub)
print(f"Harapan     : A={awal.saldo['A']-N*JUMLAH:.0f}  B={awal.saldo['B']+N*JUMLAH:.0f}  total=1500")
ok = s.total == 1500 and s.saldo["A"] == awal.saldo["A"] - N * JUMLAH and s.saldo["B"] == awal.saldo["B"] + N * JUMLAH
print("HASIL       :", "KONSISTEN" if ok else "RACE CONDITION TERJADI (saldo salah / uang hilang atau muncul)")
