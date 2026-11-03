"""L1.1 - Uji fungsi pangkat(a, b) dan akar(x)."""
import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

print("pangkat(2, 10) =", proxy.pangkat(2, 10))
print("pangkat(5, 3)  =", proxy.pangkat(5, 3))
print("akar(144)      =", proxy.akar(144))
print("akar(2)        =", proxy.akar(2))
try:
    proxy.akar(-4)
except xmlrpc.client.Fault as e:
    print("akar(-4) -> Fault:", e.faultString)
