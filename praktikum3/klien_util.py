"""Fungsi bersama untuk client Praktikum 3: transfer dengan timeout + retry backoff."""
import time
import uuid

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc


def buat_stub(alamat="localhost:50051"):
    channel = grpc.insecure_channel(alamat)
    return channel, pb_grpc.LayananNilaiStub(channel)


def transfer_dengan_retry(stub, dari, ke, jumlah, maks=3, id_baru_tiap_percobaan=False, log=print):
    """Langkah 3. id_baru_tiap_percobaan=True hanya untuk L3.2 (SALAH: memicu transfer ganda)."""
    rid = str(uuid.uuid4())                 # ID sama untuk setiap percobaan
    for percobaan in range(1, maks + 1):
        if id_baru_tiap_percobaan:
            rid = str(uuid.uuid4())         # <- L3.2: bug yang disengaja
        try:
            req = pb.TransferRequest(request_id=rid, dari=dari, ke=ke, jumlah=jumlah)
            return stub.Transfer(req, timeout=2.0)
        except grpc.RpcError as e:
            bisa_ulang = e.code() in (grpc.StatusCode.DEADLINE_EXCEEDED,
                                      grpc.StatusCode.UNAVAILABLE)
            if not bisa_ulang or percobaan == maks:
                raise
            jeda = 0.5 * 2 ** (percobaan - 1)
            log(f"    Percobaan {percobaan} gagal ({e.code().name}), ulang dalam {jeda} s")
            time.sleep(jeda)


def cetak_saldo(stub):
    s = stub.GetSaldo(pb.SaldoRequest())
    print(f"Saldo akhir : A={s.saldo['A']:.0f}  B={s.saldo['B']:.0f}  total={s.total:.0f}  "
          f"(transfer dieksekusi server: {s.jumlah_eksekusi}x)")
    return s
