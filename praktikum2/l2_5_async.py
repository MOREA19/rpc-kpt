"""L2.5 - RPC asinkron dengan stub.GetMahasiswa.future(...).
Jalankan server dengan DELAY_GET=0.2 supaya efeknya terlihat:
    DELAY_GET=0.2 python server_grpc.py
"""
import time
import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

NIM = ["2023001", "2023002"] * 5          # 10 permintaan

with grpc.insecure_channel("localhost:50051") as channel:
    stub = pb_grpc.LayananNilaiStub(channel)
    stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"))   # pemanasan koneksi

    # --- Sinkron: satu per satu (blocking) ---
    t0 = time.perf_counter()
    for nim in NIM:
        stub.GetMahasiswa(pb.MahasiswaRequest(nim=nim))
    t_sinkron = time.perf_counter() - t0

    # --- Asinkron: kirim 10 sekaligus, kumpulkan dengan .result() ---
    t0 = time.perf_counter()
    daftar_future = [stub.GetMahasiswa.future(pb.MahasiswaRequest(nim=n)) for n in NIM]
    t_kirim = time.perf_counter() - t0
    print(f"10 permintaan terkirim dalam {t_kirim*1000:.1f} ms (client tidak diblokir)")
    hasil = [f.result(timeout=5) for f in daftar_future]
    t_async = time.perf_counter() - t0

    for i, h in enumerate(hasil, 1):
        print(f"  #{i:02d} {h.nim} {h.nama:<5} IPK {h.ipk}")

    # --- Callback style (bonus) ---
    selesai = []
    f = stub.GetMahasiswa.future(pb.MahasiswaRequest(nim="2023002"))
    f.add_done_callback(lambda fut: selesai.append(fut.result().nama))
    f.result()
    time.sleep(0.05)
    print("Callback menerima nama:", selesai)

print(f"\nSinkron  (10x berurutan): {t_sinkron:.2f} s")
print(f"Asinkron (10x paralel)  : {t_async:.2f} s")
print(f"Speedup                 : {t_sinkron/t_async:.1f}x")
