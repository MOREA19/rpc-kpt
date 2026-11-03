"""L2.2 - Bidirectional streaming: ruang diskusi antar-client.

Interaktif :  python l2_2_diskusi.py Andi
Otomatis   :  python l2_2_diskusi.py Andi --otomatis "Halo semua" "Ada tugas?"
Ketik 'keluar' (mode interaktif) untuk berhenti.
"""
import queue
import sys
import threading
import time

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

nama = sys.argv[1] if len(sys.argv) > 1 else "Anonim"
otomatis = "--otomatis" in sys.argv
pesan_otomatis = sys.argv[sys.argv.index("--otomatis") + 1:] if otomatis else []
keluar = threading.Event()
kirim = queue.Queue()


def generator_pesan():
    """Stream pesan keluar: mengambil dari antrian sampai ada sinyal keluar."""
    yield pb.Pesan(pengirim=nama, isi="(bergabung)")
    while True:
        isi = kirim.get()
        if isi is None:
            return
        yield pb.Pesan(pengirim=nama, isi=isi)


def input_pengguna():
    if otomatis:
        time.sleep(1.5)                      # beri waktu peserta lain bergabung
        for isi in pesan_otomatis:
            kirim.put(isi)
            time.sleep(1)
        time.sleep(2.5)                      # tunggu balasan peserta lain
        kirim.put(None)
        return
    for baris in sys.stdin:
        baris = baris.strip()
        if baris.lower() == "keluar":
            break
        if baris:
            kirim.put(baris)
    kirim.put(None)


with grpc.insecure_channel("localhost:50051") as channel:
    stub = pb_grpc.LayananNilaiStub(channel)
    threading.Thread(target=input_pengguna, daemon=True).start()
    print(f"[{nama}] masuk ruang diskusi")
    try:
        for pesan in stub.Diskusi(generator_pesan()):   # respons datang saat peserta lain bicara
            print(f"[{nama}] <- {pesan.pengirim}: {pesan.isi}", flush=True)
    except grpc.RpcError as e:
        print("Koneksi berakhir:", e.code())
    print(f"[{nama}] keluar")
