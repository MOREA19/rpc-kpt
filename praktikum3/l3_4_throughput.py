"""L3.4 - Throughput GetMahasiswa: 200 pemanggilan dari 20 thread client,
server memakai time.sleep(0.1), max_workers = 1, 4, 10.
Skrip ini menjalankan sendiri server untuk tiap konfigurasi lalu membuat tabel + grafik.
"""
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import grpc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

TOTAL, THREAD_CLIENT, PORT = 200, 20, 50061
HASIL = []

for workers in (1, 4, 10):
    srv = subprocess.Popen([sys.executable, "server_grpc.py", "--port", str(PORT),
                            "--workers", str(workers), "--getmhs-sleep", "0.1",
                            "--slow-prob", "0"], stdout=subprocess.DEVNULL)
    channel = grpc.insecure_channel(f"localhost:{PORT}")
    grpc.channel_ready_future(channel).result(timeout=10)
    stub = pb_grpc.LayananNilaiStub(channel)
    stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"))        # pemanasan

    def panggil(_):
        t0 = time.perf_counter()
        stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"), timeout=120)
        return time.perf_counter() - t0

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=THREAD_CLIENT) as ex:
        latensi = list(ex.map(panggil, range(TOTAL)))
    total = time.perf_counter() - t0
    HASIL.append((workers, total, TOTAL / total, statistics.mean(latensi) * 1000))
    print(f"workers={workers:<2} total={total:6.2f}s throughput={TOTAL/total:6.1f} req/s "
          f"latensi rata-rata={statistics.mean(latensi)*1000:7.1f} ms", flush=True)
    channel.close()
    srv.terminate()
    srv.wait()
    time.sleep(0.5)

# ---- tabel markdown ----
tabel = ["| max_workers | Waktu total (s) | Throughput (req/s) | Latensi rata-rata (ms) |",
         "|---|---|---|---|"]
for w, t, thr, lat in HASIL:
    tabel.append(f"| {w} | {t:.2f} | {thr:.1f} | {lat:.1f} |")
open("hasil/l3_4_tabel.md", "w").write("\n".join(tabel) + "\n")
print("\n" + "\n".join(tabel))

# ---- grafik ----
w = [str(h[0]) for h in HASIL]
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
b = ax[0].bar(w, [h[2] for h in HASIL], color=["#c0392b", "#e67e22", "#27ae60"])
ax[0].set_title("Throughput vs max_workers"); ax[0].set_xlabel("max_workers"); ax[0].set_ylabel("req/s")
for r in b:
    ax[0].text(r.get_x() + r.get_width() / 2, r.get_height(), f"{r.get_height():.1f}", ha="center", va="bottom")
ax[1].plot(w, [h[3] for h in HASIL], "o-", color="#2c3e50")
ax[1].set_title("Latensi rata-rata vs max_workers"); ax[1].set_xlabel("max_workers"); ax[1].set_ylabel("ms")
for x, h in zip(w, HASIL):
    ax[1].annotate(f"{h[3]:.0f}", (x, h[3]), textcoords="offset points", xytext=(0, 8), ha="center")
fig.suptitle("L3.4 - 200 panggilan GetMahasiswa, 20 thread client, sleep server 0.1 s")
fig.tight_layout()
fig.savefig("hasil/l3_4_grafik.png", dpi=150)
print("Grafik disimpan di hasil/l3_4_grafik.png")
