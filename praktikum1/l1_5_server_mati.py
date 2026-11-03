"""L1.5 - Client yang tangguh ketika server dimatikan.
Cara uji: jalankan server, jalankan client ini, lalu matikan server (Ctrl+C)
saat client masih berjalan, lalu hidupkan lagi untuk melihat client pulih.
"""
import http.client
import time
import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")


def panggil_aman(fungsi, *args, percobaan=3, jeda=1.0):
    for ke in range(1, percobaan + 1):
        try:
            return fungsi(*args)
        except ConnectionRefusedError as e:
            print(f"  [{type(e).__name__}] server tidak berjalan / port tertutup")
        except (http.client.RemoteDisconnected, ConnectionResetError, BrokenPipeError) as e:
            print(f"  [{type(e).__name__}] koneksi diputus server di tengah panggilan")
        except xmlrpc.client.ProtocolError as e:
            print(f"  [ProtocolError] HTTP {e.errcode} {e.errmsg}")
        except xmlrpc.client.Fault as e:   # error logika dari server, jangan di-retry
            print(f"  [Fault] {e.faultString}")
            return None
        except OSError as e:
            print(f"  [{type(e).__name__}] {e}")
        if ke < percobaan:
            print(f"  ulang dalam {jeda}s (percobaan {ke}/{percobaan})")
            time.sleep(jeda)
    print("  GAGAL: server tidak dapat dihubungi")
    return None


if __name__ == "__main__":
    for i in range(1, 16):
        print(f"Panggilan {i}: tambah({i}, 10)")
        hasil = panggil_aman(proxy.tambah, i, 10)
        print("  hasil =", hasil)
        time.sleep(1)
