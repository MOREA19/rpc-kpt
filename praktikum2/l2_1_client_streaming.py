"""L2.1 - Client streaming: KirimBanyakNilai(stream NilaiRequest) -> StatusResponse."""
import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc


def generator_nilai():
    data = [
        ("2023002", "Jaringan", 80),
        ("2023002", "Sistem Operasi", 75.5),
        ("2023002", "Komputasi Paralel", 90),
        ("2023003", "Basis Data", 70),
        ("2023003", "Jaringan", 150),   # tidak valid -> akan ditolak server
    ]
    for nim, matkul, nilai in data:
        print(f"  mengirim {nim} {matkul} = {nilai}")
        yield pb.NilaiRequest(nim=nim, matkul=matkul, nilai=nilai)


with grpc.insecure_channel("localhost:50051") as channel:
    stub = pb_grpc.LayananNilaiStub(channel)
    print("Mengirim banyak nilai (client streaming):")
    resp = stub.KirimBanyakNilai(generator_nilai())
    print("Respons server:", resp.sukses, "-", resp.pesan)

    print("\nVerifikasi dengan StreamNilai(2023002):")
    for n in stub.StreamNilai(pb.MahasiswaRequest(nim="2023002")):
        print(f"  {n.matkul}: {n.nilai}")
