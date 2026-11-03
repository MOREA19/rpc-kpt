"""L3.5 (Pengayaan) - Client failover: pindah ke server berikutnya bila UNAVAILABLE.
Jalankan dua server:  python server_grpc.py --port 50051 --slow-prob 0
                      python server_grpc.py --port 50052 --slow-prob 0
Lalu jalankan client ini dan matikan server pertama saat berjalan.
"""
import sys
import time

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

SERVERS = ["localhost:50051", "localhost:50052"]


class FailoverClient:
    def __init__(self, alamat):
        self.alamat = alamat
        self.channels = [grpc.insecure_channel(a) for a in alamat]
        self.stubs = [pb_grpc.LayananNilaiStub(c) for c in self.channels]
        self.aktif = 0                        # indeks server yang sedang dipakai

    def panggil(self, nama_rpc, request, timeout=2.0):
        n = len(self.stubs)
        for coba in range(n):                 # coba tiap server paling banyak satu kali
            i = (self.aktif + coba) % n
            try:
                hasil = getattr(self.stubs[i], nama_rpc)(request, timeout=timeout)
                if i != self.aktif:
                    print(f"  >> FAILOVER: pindah dari {self.alamat[self.aktif]} ke {self.alamat[i]}")
                    self.aktif = i
                return hasil, self.alamat[i]
            except grpc.RpcError as e:
                if e.code() not in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED):
                    raise                     # error logika (NOT_FOUND dll) jangan di-failover
                print(f"  !! {self.alamat[i]} {e.code().name}")
        raise ConnectionError("Semua server tidak tersedia")


if __name__ == "__main__":
    jumlah = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    client = FailoverClient(SERVERS)
    for k in range(1, jumlah + 1):
        try:
            mhs, dari = client.panggil("GetMahasiswa", pb.MahasiswaRequest(nim="2023001"))
            print(f"#{k:02d} dijawab oleh {dari}: {mhs.nama} IPK {mhs.ipk}", flush=True)
        except ConnectionError as e:
            print(f"#{k:02d} {e}", flush=True)
        time.sleep(1)
