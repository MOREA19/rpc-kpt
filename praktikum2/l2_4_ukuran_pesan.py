"""L2.4 - Bandingkan ukuran pesan Protobuf vs XML-RPC (data yang sama)."""
import json
import xmlrpc.client

import akademik_pb2 as pb

nim, nama, ipk = "2023001", "Andi", 3.26

# --- Protobuf ---
mhs = pb.Mahasiswa(nim=nim, nama=nama, ipk=ipk)
ukuran_pb = len(mhs.SerializeToString())
print("Protobuf bytes :", mhs.SerializeToString())

# --- XML-RPC: response berisi struct dengan data yang sama ---
xml_resp = xmlrpc.client.dumps(({"nim": nim, "nama": nama, "ipk": ipk},), methodresponse=True)
ukuran_xml = len(xml_resp.encode("utf-8"))

# --- Pembanding tambahan: JSON ---
ukuran_json = len(json.dumps({"nim": nim, "nama": nama, "ipk": ipk}, separators=(",", ":")).encode())

# --- Request-nya juga dibandingkan ---
req_pb = len(pb.MahasiswaRequest(nim=nim).SerializeToString())
req_xml = len(xmlrpc.client.dumps((nim,), methodname="get_mahasiswa").encode("utf-8"))

print(f"\n{'Pesan':<28}{'Ukuran (byte)':>14}")
print("-" * 42)
print(f"{'Respons Protobuf':<28}{ukuran_pb:>14}")
print(f"{'Respons JSON (pembanding)':<28}{ukuran_json:>14}")
print(f"{'Respons XML-RPC':<28}{ukuran_xml:>14}")
print(f"{'Request Protobuf':<28}{req_pb:>14}")
print(f"{'Request XML-RPC':<28}{req_xml:>14}")
print(f"\nXML-RPC {ukuran_xml/ukuran_pb:.1f}x lebih besar dari Protobuf (respons)")
print(f"XML-RPC {req_xml/req_pb:.1f}x lebih besar dari Protobuf (request)")
print(f"Protobuf menghemat {(1-ukuran_pb/ukuran_xml)*100:.1f}% ukuran")
