"""L1.3 - Parameter datetime dan bilangan > 2^31 (batas int XML-RPC)."""
import datetime
import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

print("--- 1. Objek datetime ---")
sekarang = datetime.datetime(2026, 11, 2, 9, 30, 15)
print("XML:", xmlrpc.client.dumps((sekarang,), methodname="info_tipe").split("<params>")[1][:90])
print("Server menerima:", proxy.info_tipe(sekarang))

print("\n--- 2. Bilangan dalam batas 32-bit (2^31 - 1) ---")
print(proxy.tambah(2**31 - 1, 0))

print("\n--- 3. Bilangan > 2^31 ---")
besar = 2**31 + 5
try:
    print(proxy.tambah(besar, 1))
except OverflowError as e:
    print("OverflowError di CLIENT (sebelum dikirim):", e)

print("\n--- 4. Solusi A: kirim sebagai string ---")
print("Server menerima:", proxy.info_tipe(str(besar)))

print("\n--- 5. Solusi B: kirim sebagai float (double) ---")
print("tambah(float) =", proxy.tambah(float(besar), 1.0))
