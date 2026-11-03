"""L1.4 - Bandingkan 100x tambah() via RPC vs fungsi lokal.
Pakai:  python l1_4_benchmark.py            (localhost)
        python l1_4_benchmark.py 192.168.1.10   (server di komputer lain)
"""
import sys
import time
import xmlrpc.client

HOST = sys.argv[1] if len(sys.argv) > 1 else "localhost"
N = 100


def tambah_lokal(a, b):
    return a + b


proxy = xmlrpc.client.ServerProxy(f"http://{HOST}:8000/")
proxy.tambah(1, 1)  # pemanasan koneksi

t0 = time.perf_counter()
for i in range(N):
    tambah_lokal(i, i)
t_lokal = time.perf_counter() - t0

t0 = time.perf_counter()
for i in range(N):
    proxy.tambah(i, i)
t_rpc = time.perf_counter() - t0

print(f"Host server        : {HOST}")
print(f"{N}x fungsi lokal   : {t_lokal*1000:.4f} ms (rata-rata {t_lokal/N*1e6:.3f} us/panggilan)")
print(f"{N}x RPC XML-RPC    : {t_rpc*1000:.2f} ms (rata-rata {t_rpc/N*1000:.3f} ms/panggilan)")
print(f"RPC lebih lambat   : {t_rpc/t_lokal:,.0f}x")
