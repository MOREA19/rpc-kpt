"""L2.3 - CLIENT LAMA: memakai stub yang digenerate dari proto TANPA field prodi.
Dijalankan terhadap SERVER BARU (yang sudah mengirim field prodi = 4)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "v1_lama"))

import grpc
import akademik_pb2 as pb          # <- stub lama
import akademik_pb2_grpc as pb_grpc

print("Field yang dikenal client lama:", [f.name for f in pb.Mahasiswa.DESCRIPTOR.fields])

with grpc.insecure_channel("localhost:50051") as channel:
    stub = pb_grpc.LayananNilaiStub(channel)
    mhs = stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"))
    print(f"Berhasil: {mhs.nama} - IPK {mhs.ipk}")
    print("Ada atribut 'prodi' di client lama?", hasattr(mhs, "prodi"))
    # Field 4 tidak hilang: disimpan sebagai unknown field & ikut ter-serialisasi ulang
    ulang = mhs.SerializeToString()
    print("Serialisasi ulang oleh client lama:", len(ulang), "byte ->", ulang)
    print("(byte 'Informatika' masih ada = field 4 disimpan sebagai unknown field)")
    print(stub.TambahNilai(pb.NilaiRequest(nim="2023001", matkul="PBO", nilai=90)).pesan)
