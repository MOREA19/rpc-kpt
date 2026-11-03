"""L1.2 - Marshalling list & dictionary. Cetak XML request/response asli."""
import xmlrpc.client

data = [70, 85.5, 90, 60, 100]

# Bentuk XML request yang dibuat client stub (marshalling):
print("=== XML REQUEST (hasil marshalling list) ===")
print(xmlrpc.client.dumps((data,), methodname="statistik"))

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")
hasil = proxy.statistik(data)
print("=== HASIL (dictionary hasil unmarshalling) ===")
print(hasil)

# Bentuk XML response yang dibuat server stub (dictionary -> <struct>):
print("\n=== XML RESPONSE (hasil marshalling dictionary) ===")
print(xmlrpc.client.dumps((hasil,), methodresponse=True))
