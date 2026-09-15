# kajian-data

Data jadwal kajian rutin mingguan untuk aplikasi **Ritme** (ritme.quickorganize.id). Diperbarui otomatis setiap hari oleh agen Claude (lihat `AGENT.md`).

- `kajian.json` — berkas yang dibaca aplikasi. Jangan diedit manual saat agen berjalan; kalau perlu koreksi, edit lalu commit — agen akan menghormati perubahan sampai sumbernya berkata lain.
- `hasil/<wilayah>.json` — hasil crawl mentah per wilayah (ditimpa tiap putaran).
- `gabung.py` — menggabung `hasil/*` ke `kajian.json` (dedupe, kadaluarsa 24 bulan).
- `giliran.py` — memilih 2 wilayah per hari (12 wilayah, siklus 6 hari).
- `AGENT.md` — instruksi lengkap agen. Ubah perilaku agen = ubah berkas ini.

Skema entri: `id, judul, pemateri, lokasi, alamat, kota, hari (1=Senin…7=Ahad), mulai, selesai, kategori, deskripsi, sumber[], terakhir_terlihat, pertama_terlihat, confidence (tinggi|sedang|rendah)`.
