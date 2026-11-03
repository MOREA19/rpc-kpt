"""L3.1 & L3.2 - 20x transfer 10 dari A ke B secara berurutan.

  python l3_1_l3_2_transfer.py            # L3.1: ID permintaan SAMA tiap percobaan (benar)
  python l3_1_l3_2_transfer.py --uuid-baru   # L3.2: ID BARU tiap percobaan (salah)
"""
import sys
import akademik_pb2 as pb
from klien_util import buat_stub, cetak_saldo, transfer_dengan_retry

uuid_baru = "--uuid-baru" in sys.argv
N, JUMLAH = 20, 10.0
channel, stub = buat_stub()

print(f"Mode: {'L3.2 - uuid BARU tiap percobaan (SALAH)' if uuid_baru else 'L3.1 - uuid SAMA tiap percobaan (BENAR)'}")
awal = stub.GetSaldo(pb.SaldoRequest())
print(f"Saldo awal  : A={awal.saldo['A']:.0f}  B={awal.saldo['B']:.0f}  total={awal.total:.0f}")

gagal = 0
for i in range(1, N + 1):
    print(f"Transfer #{i:02d}")
    try:
        transfer_dengan_retry(stub, "A", "B", JUMLAH, id_baru_tiap_percobaan=uuid_baru)
    except Exception as e:
        gagal += 1
        print("    GAGAL TOTAL:", getattr(e, "code", lambda: e)())

s = cetak_saldo(stub)
berkurang = awal.saldo["A"] - s.saldo["A"]
print(f"\nA berkurang  : {berkurang:.0f}  (seharusnya {N*JUMLAH:.0f})")
print(f"Total saldo  : {s.total:.0f}  (seharusnya 1500)")
print("HASIL        :", "BENAR (tepat satu kali per transfer)" if berkurang == N * JUMLAH and gagal == 0
      else f"TRANSFER GANDA / TIDAK KONSISTEN (kelebihan {berkurang - N*JUMLAH:.0f})")
