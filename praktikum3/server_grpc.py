"""Praktikum 3 - Server gRPC dengan Transfer (deduplikasi at-most-once),
respons lambat acak, opsi tanpa-lock, dan jumlah worker yang bisa diatur.

Contoh:
  python server_grpc.py                                 # perilaku default Langkah 2
  python server_grpc.py --no-lock --race-delay 0.001 --slow-prob 0    # L3.3
  python server_grpc.py --workers 4 --getmhs-sleep 0.1 --slow-prob 0  # L3.4
  python server_grpc.py --port 50052                                  # L3.5
"""
import argparse
import contextlib
import random
import threading
import time
from concurrent import futures

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

ap = argparse.ArgumentParser()
ap.add_argument("--port", type=int, default=50051)
ap.add_argument("--workers", type=int, default=10, help="max_workers ThreadPoolExecutor")
ap.add_argument("--no-lock", action="store_true", help="L3.3: hapus with LOCK")
ap.add_argument("--race-delay", type=float, default=0.0,
                help="jeda (detik) antara baca & tulis saldo; memperlebar jendela race condition")
ap.add_argument("--slow-prob", type=float, default=0.3, help="peluang balasan terlambat")
ap.add_argument("--slow-sec", type=float, default=3.0, help="lama keterlambatan balasan")
ap.add_argument("--getmhs-sleep", type=float, default=0.0, help="L3.4: sleep di GetMahasiswa")
ap.add_argument("--seed", type=int, default=None)
ARGS = ap.parse_args()
if ARGS.seed is not None:
    random.seed(ARGS.seed)

DATA = {
    "2023001": {"nama": "Andi", "nilai": {"Basis Data": 85.0, "Jaringan": 78.0}},
    "2023002": {"nama": "Sari", "nilai": {"Basis Data": 92.0}},
}
SALDO = {"A": 1000.0, "B": 500.0}
PROSES = {}                      # request_id -> StatusResponse yang sudah dikirim
EKSEKUSI = 0                     # berapa kali transfer BENAR-BENAR dijalankan
LOCK = threading.Lock()
# --no-lock  => with LOCK diganti context manager kosong (tidak mengunci apa pun)
KUNCI = contextlib.nullcontext() if ARGS.no_lock else LOCK


class LayananNilai(pb_grpc.LayananNilaiServicer):
    def GetMahasiswa(self, request, context):
        if ARGS.getmhs_sleep:
            time.sleep(ARGS.getmhs_sleep)
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"NIM {request.nim} tidak ditemukan")
        daftar = list(mhs["nilai"].values())
        ipk = sum(daftar) / len(daftar) / 25 if daftar else 0.0
        return pb.Mahasiswa(nim=request.nim, nama=mhs["nama"], ipk=round(ipk, 2))

    def TambahNilai(self, request, context):
        if not 0 <= request.nilai <= 100:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Nilai harus 0-100")
        mhs = DATA.setdefault(request.nim, {"nama": "(baru)", "nilai": {}})
        mhs["nilai"][request.matkul] = request.nilai
        return pb.StatusResponse(sukses=True, pesan="Nilai tersimpan")

    def StreamNilai(self, request, context):
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "NIM tidak ditemukan")
        for matkul, nilai in mhs["nilai"].items():
            yield pb.Nilai(matkul=matkul, nilai=nilai)
            time.sleep(0.5)

    def Transfer(self, request, context):
        global EKSEKUSI
        with KUNCI:
            if request.request_id in PROSES:                 # permintaan duplikat
                print(f"[server:{ARGS.port}] DUPLIKAT {request.request_id[:8]} -> balasan lama dikirim ulang", flush=True)
                return PROSES[request.request_id]
            if request.dari not in SALDO or request.ke not in SALDO:
                hasil = pb.StatusResponse(sukses=False, pesan="Akun tidak dikenal")
            elif SALDO[request.dari] < request.jumlah:
                hasil = pb.StatusResponse(sukses=False, pesan="Saldo tidak cukup")
            else:
                # baca -> (jeda) -> tulis: sengaja dipisah agar race condition bisa diamati
                a = SALDO[request.dari]
                if ARGS.race_delay:
                    time.sleep(ARGS.race_delay)
                SALDO[request.dari] = a - request.jumlah
                b = SALDO[request.ke]
                if ARGS.race_delay:
                    time.sleep(ARGS.race_delay)
                SALDO[request.ke] = b + request.jumlah
                EKSEKUSI += 1
                hasil = pb.StatusResponse(sukses=True, pesan=f"Saldo kini {SALDO}")
            PROSES[request.request_id] = hasil
            print(f"[server:{ARGS.port}] TRANSFER {request.request_id[:8]} {request.dari}->{request.ke} {request.jumlah}", flush=True)
        if random.random() < ARGS.slow_prob:
            time.sleep(ARGS.slow_sec)        # simulasi balasan terlambat: transfer SUDAH terjadi
        return hasil

    def GetSaldo(self, request, context):
        with LOCK:
            return pb.SaldoResponse(saldo=dict(SALDO), total=sum(SALDO.values()),
                                    jumlah_eksekusi=EKSEKUSI)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=ARGS.workers))
    pb_grpc.add_LayananNilaiServicer_to_server(LayananNilai(), server)
    server.add_insecure_port(f"[::]:{ARGS.port}")
    server.start()
    print(f"Server gRPC berjalan di port {ARGS.port} (workers={ARGS.workers}, "
          f"lock={'OFF' if ARGS.no_lock else 'ON'})...", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
