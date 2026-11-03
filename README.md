# Latihan & Praktikum Remote Procedure Calls (RPC)

| | |
|---|---|
| Nama | Adithya Nurrahman |
| NIM | 247006111176 |
| Kelas | F |
| Mata kuliah | Komputasi Paralel dan Terdistribusi (KPT) |
| Cakupan | Latihan Praktikum 1 (XML-RPC), 2 (gRPC), dan 3 (Concurrency, Timeout, Toleransi Kegagalan) |

## Isi folder

```
KPT_RPC/
├── README.md                      <- file ini
├── requirements.txt
├── praktikum1/   (XML-RPC)        <- kode L1.1 - L1.5 + hasil/
├── praktikum2/   (gRPC)           <- kode L2.1 - L2.5 + hasil/
└── praktikum3/   (gRPC lanjutan)  <- kode L3.1 - L3.5 + hasil/
```

Setiap laporan mengikuti format modul: identitas, tujuan & dasar teori, langkah kerja + kode,
hasil eksekusi, jawaban pertanyaan analisis, kesimpulan & kendala. Berkas `.docx` disediakan
agar tangkapan layar dapat ditempel pada kotak **[TANGKAPAN LAYAR n]**, lalu diekspor ulang ke PDF
dengan nama `NIM_Praktikum-RPC-<nomor>.pdf`.

## Persiapan

```bash
python3 --version            # minimal 3.10
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Stub gRPC (`akademik_pb2*.py`) sudah disertakan. Bila `.proto` diubah, generate ulang:
`python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. akademik.proto`

> Dua komputer: ganti `localhost` pada client dengan IP server (L1.4 menerima IP sebagai argumen)
> dan pastikan port 8000 / 50051 tidak diblokir firewall.

## Peta latihan -> berkas -> cara menjalankan

Jalankan server di terminal 1, skrip latihan di terminal 2.

### Praktikum 1 (`cd praktikum1`, server: `python server_kalkulator.py`)

| Latihan | Berkas | Perintah |
|---|---|---|
| Langkah 2-3 | `client_kalkulator.py` | `python client_kalkulator.py` |
| L1.1 pangkat & akar | `l1_1_pangkat_akar.py` | `python l1_1_pangkat_akar.py` |
| L1.2 statistik (list & dict) | `l1_2_statistik.py` | `python l1_2_statistik.py` |
| L1.3 datetime & bilangan > 2^31 | `l1_3_datetime_bigint.py` | `python l1_3_datetime_bigint.py` |
| L1.4 benchmark 100x | `l1_4_benchmark.py` | `python l1_4_benchmark.py [IP-server]` |
| L1.5 server dimatikan | `l1_5_server_mati.py` | `python l1_5_server_mati.py` lalu matikan/hidupkan server |
| Analisis ukuran XML | `analisis_ukuran.py` | `python analisis_ukuran.py` |

### Praktikum 2 (`cd praktikum2`, server: `python server_grpc.py`)

| Latihan | Berkas | Perintah |
|---|---|---|
| Langkah 4 | `client_grpc.py` | `python client_grpc.py` |
| L2.1 client streaming | `l2_1_client_streaming.py` | `python l2_1_client_streaming.py` |
| L2.2 bidirectional streaming | `l2_2_diskusi.py` | `python l2_2_diskusi.py Andi` (terminal 2) dan `python l2_2_diskusi.py Sari` (terminal 3) |
| L2.3 backward compatibility | `l2_3_compat/client_lama.py` | `python l2_3_compat/client_lama.py` (stub lama di `v1_lama/`) |
| L2.4 ukuran pesan | `l2_4_ukuran_pesan.py` | `python l2_4_ukuran_pesan.py` |
| L2.5 RPC asinkron | `l2_5_async.py` | server: `DELAY_GET=0.2 python server_grpc.py`, lalu `python l2_5_async.py` |

### Praktikum 3 (`cd praktikum3`)

| Latihan | Server | Client |
|---|---|---|
| L3.1 (uuid sama) | `python server_grpc.py --seed 7` | `python l3_1_l3_2_transfer.py` |
| L3.2 (uuid baru) | `python server_grpc.py --seed 7` (restart) | `python l3_1_l3_2_transfer.py --uuid-baru` |
| L3.3a tanpa lock | `python server_grpc.py --no-lock --slow-prob 0` | `python l3_3_concurrent.py` |
| L3.3b tanpa lock + jeda race | `python server_grpc.py --no-lock --race-delay 0.001 --slow-prob 0` | `python l3_3_concurrent.py` |
| L3.3c dengan lock (pembanding) | `python server_grpc.py --race-delay 0.001 --slow-prob 0` | `python l3_3_concurrent.py` |
| L3.4 throughput | (dijalankan otomatis oleh skrip) | `python l3_4_throughput.py` |
| L3.5 failover | `python server_grpc.py --port 50051 --slow-prob 0` dan `... --port 50052 --slow-prob 0` | `python l3_5_failover.py` (matikan server 50051 saat berjalan) |

**Restart server di antara percobaan** agar saldo kembali ke A=1000, B=500.

## Catatan

- Semua angka pada `hasil/` dan laporan berasal dari eksekusi pada satu mesin (localhost). Waktu/throughput
  di komputer Anda akan berbeda; jalankan ulang lalu isi bagian "dua komputer" pada L1.4.
- `--race-delay` pada L3.3 hanya memperlebar jendela *race condition* agar kesalahan terlihat;
  tanpa jeda, GIL Python membuat race jarang muncul meski bug-nya tetap ada.
- RPC `GetSaldo` pada Praktikum 3 adalah tambahan (di luar modul) untuk memverifikasi saldo akhir.
- Tangkapan layar tidak dapat dibuat otomatis; ambil sendiri dari terminal Anda sesuai penanda pada laporan.
