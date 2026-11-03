"""Praktikum 2 - Server gRPC: unary, server streaming (Langkah 3)
plus L2.1 (client streaming) dan L2.2 (bidirectional streaming)."""
import os
import queue
import threading
import time
from concurrent import futures

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

DATA = {
    "2023001": {"nama": "Andi", "nilai": {"Basis Data": 85.0, "Jaringan": 78.0}},
    "2023002": {"nama": "Sari", "nilai": {"Basis Data": 92.0}},
}
DATA_LOCK = threading.Lock()
# Simulasi waktu proses GetMahasiswa (detik); dipakai di L2.5. Atur lewat env.
DELAY_GET = float(os.environ.get("DELAY_GET", "0"))


def hitung_ipk(daftar):
    return sum(daftar) / len(daftar) / 25 if daftar else 0.0  # konversi 0-100 ke 0-4


class LayananNilai(pb_grpc.LayananNilaiServicer):
    def __init__(self):
        # L2.2: setiap peserta diskusi punya satu antrian pesan keluar
        self._peserta = set()
        self._peserta_lock = threading.Lock()

    # ---------- unary ----------
    def GetMahasiswa(self, request, context):
        if DELAY_GET:
            time.sleep(DELAY_GET)
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"NIM {request.nim} tidak ditemukan")
        ipk = hitung_ipk(list(mhs["nilai"].values()))
        return pb.Mahasiswa(nim=request.nim, nama=mhs["nama"],
                            ipk=round(ipk, 2), prodi="Informatika")

    def TambahNilai(self, request, context):
        if not 0 <= request.nilai <= 100:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Nilai harus 0-100")
        with DATA_LOCK:
            mhs = DATA.setdefault(request.nim, {"nama": "(baru)", "nilai": {}})
            mhs["nilai"][request.matkul] = request.nilai
        return pb.StatusResponse(sukses=True, pesan="Nilai tersimpan")

    # ---------- server streaming ----------
    def StreamNilai(self, request, context):
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "NIM tidak ditemukan")
        for matkul, nilai in list(mhs["nilai"].items()):
            yield pb.Nilai(matkul=matkul, nilai=nilai)
            time.sleep(0.5)  # simulasi data dikirim bertahap

    # ---------- L2.1 client streaming ----------
    def KirimBanyakNilai(self, request_iterator, context):
        tersimpan = ditolak = 0
        for req in request_iterator:          # membaca stream dari client satu per satu
            if not 0 <= req.nilai <= 100:
                ditolak += 1
                continue
            with DATA_LOCK:
                mhs = DATA.setdefault(req.nim, {"nama": "(baru)", "nilai": {}})
                mhs["nilai"][req.matkul] = req.nilai
            tersimpan += 1
        pesan = f"{tersimpan} nilai tersimpan" + (f", {ditolak} ditolak" if ditolak else "")
        return pb.StatusResponse(sukses=tersimpan > 0, pesan=pesan)

    # ---------- L2.2 bidirectional streaming ----------
    def Diskusi(self, request_iterator, context):
        antrian = queue.Queue()
        with self._peserta_lock:
            self._peserta.add(antrian)

        def baca_dari_client():
            nama = "?"
            try:
                for pesan in request_iterator:
                    nama = pesan.pengirim
                    print(f"[diskusi] {pesan.pengirim}: {pesan.isi}")
                    with self._peserta_lock:           # siarkan ke semua peserta lain
                        for q in self._peserta:
                            if q is not antrian:
                                q.put(pesan)
            except grpc.RpcError:
                pass
            finally:                                    # client selesai / terputus
                with self._peserta_lock:
                    self._peserta.discard(antrian)
                print(f"[diskusi] {nama} keluar dari ruang diskusi")
                antrian.put(None)                       # sinyal berhenti

        threading.Thread(target=baca_dari_client, daemon=True).start()
        while context.is_active():
            try:
                pesan = antrian.get(timeout=0.5)
            except queue.Empty:
                continue
            if pesan is None:
                break
            yield pesan


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    pb_grpc.add_LayananNilaiServicer_to_server(LayananNilai(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server gRPC berjalan di port 50051...", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
