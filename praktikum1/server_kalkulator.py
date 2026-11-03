"""Praktikum 1 - Server XML-RPC (kalkulator + latihan L1.1 s.d. L1.3)."""
import math
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer


def tambah(a, b):
    return a + b


def kali(a, b):
    return a * b


def bagi(a, b):
    if b == 0:
        raise ValueError("Pembagian dengan nol")
    return a / b


# ---- L1.1 ----
def pangkat(a, b):
    return a ** b


def akar(x):
    if x < 0:
        raise ValueError("Akar dari bilangan negatif")
    return math.sqrt(x)


# ---- L1.2 ----
def statistik(daftar):
    if not daftar:
        raise ValueError("Daftar kosong")
    return {"min": min(daftar), "max": max(daftar),
            "rata2": sum(daftar) / len(daftar)}


# ---- L1.3 ----
def info_tipe(nilai):
    """Mengembalikan tipe Python yang DITERIMA server (bukti hasil unmarshalling)."""
    if isinstance(nilai, xmlrpc.client.DateTime):
        return f"xmlrpc.client.DateTime -> {nilai}"
    return f"{type(nilai).__name__} -> {nilai!r}"


if __name__ == "__main__":
    server = SimpleXMLRPCServer(("0.0.0.0", 8000), allow_none=True,
                                logRequests=True)
    server.register_introspection_functions()
    for fungsi in (tambah, kali, bagi, pangkat, akar, statistik, info_tipe):
        server.register_function(fungsi, fungsi.__name__)
    print("Server XML-RPC berjalan di port 8000...")
    server.serve_forever()
