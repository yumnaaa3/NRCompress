# DataKompresi - Aplikasi Kompresi File

Aplikasi web untuk mengompresi file teks menggunakan berbagai algoritma kompresi seperti Huffman Coding, Run-Length Encoding (RLE), dan LZW Compression.

## Fitur

- Upload file teks (.txt)
- Pilihan algoritma kompresi:
  - Huffman Coding
  - Run-Length Encoding (RLE)
  - LZW Compression
- Tampilan hasil kompresi (ukuran sebelum dan sesudah)
- Download file hasil kompresi
- Antarmuka yang modern dan responsif

## Persyaratan Sistem

- Python 3.8 atau lebih baru
- pip (Python package manager)

## Instalasi

1. Clone repository ini:
```bash
git clone https://github.com/username/datakompresi.git
cd datakompresi
```

2. Buat virtual environment (opsional tapi direkomendasikan):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

1. Pastikan virtual environment aktif (jika menggunakan)

2. Jalankan aplikasi Flask:
```bash
python app.py
```

3. Buka browser dan akses:
```
http://localhost:5000
```

## Penggunaan

1. Buka aplikasi di browser
2. Pilih file teks (.txt) yang ingin dikompresi
3. Pilih algoritma kompresi yang diinginkan
4. Klik tombol "Kompresi File"
5. Tunggu proses kompresi selesai
6. Lihat hasil kompresi dan download file hasil jika diinginkan

## Struktur Proyek

```
datakompresi/
├── app.py              # Backend Flask
├── requirements.txt    # Dependencies Python
├── static/            # File statis
│   ├── style.css      # Styling
│   └── script.js      # JavaScript
└── templates/         # Template HTML
    └── index.html     # Halaman utama
```

## Kontribusi

Silakan buat pull request untuk kontribusi. Untuk perubahan besar, harap buka issue terlebih dahulu untuk mendiskusikan perubahan yang diinginkan.

## Lisensi

[MIT](https://choosealicense.com/licenses/mit/) 