"""Pertanyaan analisis P1 - ukuran pesan XML untuk tambah(5, 3)."""
import re
import xmlrpc.client

req = xmlrpc.client.dumps((5, 3), methodname="tambah")
res = xmlrpc.client.dumps((8,), methodresponse=True)

# "Data sebenarnya" = nama method + nilai parameter/hasil (karakter yang bermakna)
data_req = len("tambah") + len("5") + len("3")
data_res = len("8")

for nama, pesan, data in (("methodCall (request)", req, data_req),
                          ("methodResponse (response)", res, data_res)):
    ukuran = len(pesan.encode("utf-8"))
    print(f"=== {nama} ===")
    print(pesan)
    print(f"Ukuran XML     : {ukuran} byte")
    print(f"Data sebenarnya: {data} byte ({data/ukuran*100:.1f}%)")
    print(f"Overhead format: {ukuran-data} byte ({(ukuran-data)/ukuran*100:.1f}%)\n")
