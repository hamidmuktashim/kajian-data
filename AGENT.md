# AGENT.md — Agen crawler jadwal kajian rutin (dijalankan otomatis setiap hari)

Kamu adalah agen otomatis. Tidak ada manusia yang menunggu jawaban — jangan bertanya, ambil keputusan sendiri sesuai aturan di sini, dan akhiri dengan laporan singkat.
Tujuan: menjaga `kajian.json` di repo ini tetap segar. Aplikasi Ritme (ritme.quickorganize.id) membaca berkas itu langsung; apa pun yang kamu tulis akan tampil ke pengguna. **Kesalahan = orang datang ke masjid yang salah.** Lebih baik kosong daripada mengarang.

## 0. Persiapan
1. Repo sudah di-clone di direktori kerja. Jalankan `git pull --ff-only`.
2. Baca `kajian.json` — perhatikan entri untuk wilayah yang kamu kerjakan hari ini (untuk diverifikasi ulang, bukan dibuat ulang).
3. Tentukan wilayah hari ini: `python3 giliran.py` mencetak 2 slug wilayah. Kerjakan HANYA itu.

## 1. Wilayah dan sumber yang wajib dicoba
Kanal Telegram `t.me/s/jadwalkajianID` (milik akun Instagram jadwalkajiansunnahindonesia) memuat puluhan post per hari untuk Jabodetabek — teks + poster; baca **teksnya**, dan untuk wilayah Jabodetabek buka juga halaman sebelumnya (`t.me/s/jadwalkajianID?before=<id post terlama di halaman>`) sampai ±3 halaman supaya tidak hanya dapat post hari ini. Pisahkan post "rutin/setiap" (→ `kajian`) dari post bertanggal (→ `agenda`).

Selalu tambahkan pencarian web umum: `"jadwal kajian rutin <wilayah> setiap"`, `"kajian rutin masjid <wilayah> pekanan 2026"`, `"jadwal kajian <wilayah> minggu ini"` — buka 3–5 hasil terbaik. Sumber yang ternyata 404 dua kali berturut-turut boleh kamu catat di `sumber-mati.txt` supaya tidak dicoba lagi selama 30 hari.

| slug | wilayah | sumber khusus |
|---|---|---|
| bandung-kota | Kota Bandung | tarbiyahsunnah.com/event_tag/kajian-rutin/ · kajiansunnahbandung.web.id · t.me/s/infokajianbandung · kabarharmoni.com (Al-Lathiif) · almultazambandung.com/jadwal-kajian · masjidrayaaljabbar.com · t.me/s/markazilmuofficial (agenda bertanggal Bandung) |
| bandung-kab | Kab. Bandung, Cimahi, Cileunyi, Soreang | tarbiyahsunnah.com · kajiansunnahbandung.web.id/jadwal-kajian-rutin-bandung-timur-dan-sekitarnya/ · sunnah.me |
| jaksel | Jakarta Selatan | masjidagungalazhar.com/program/majelis-taklim-kajian-rutin-masjid-agung-al-azhar · majlis.id/organizers/masjid-nurul%20iman%20blok%20m%20square · t.me/s/jadwalkajianID · alsofwa.com · masjidrayapondokindah.com |
| jakpus-jakut | Jakarta Pusat & Utara | t.me/s/jadwalkajianID · majlis.id · masjid Istiqlal (istiqlal.or.id) · Masjid Sunda Kelapa (masjidsundakelapa.or.id) · Masjid Ramlie Musofa |
| jaktim-jakbar | Jakarta Timur & Barat | t.me/s/jadwalkajianID · majlis.id · jadwalkajian.com/jadwal-kajian/jakarta-timur/ · Masjid Al-Barkah Bekasi Timur (berbatasan) |
| bogor | Kota & Kab. Bogor | jadwalkajian.com/jadwal-kajian/bogor/ · Masjid Raya Bogor · Masjid Al-Hasanah · t.me/s/jadwalkajianID |
| depok | Depok | jadwalkajian.com/jadwal-kajian/depok/ · Masjid Kubah Emas · Masjid Al-Ihsan UI · t.me/s/jadwalkajianID |
| tangerang | Kota Tangerang & Tangsel | jadwalkajian.com/jadwal-kajian/tangerang/ · Masjid Raya Bintaro · Masjid Al-Azhar BSD · t.me/s/jadwalkajianID |
| bekasi | Kota & Kab. Bekasi | t.me/s/jadwalkajianID (paling produktif untuk Bekasi) · jadwalkajian.com/jadwal-kajian/bekasi/ · Masjid Al-Barkah · Masjid Agung Al-Azhar Jakapermai |
| surabaya | Surabaya | Masjid Al-Akbar (masjidalakbar.or.id) · Masjid Al-Falah Surabaya · pencarian "kajian rutin surabaya" · Telegram publik kajian surabaya |
| yogyakarta | Yogyakarta & Sleman | Masjid Jogokariyan (masjidjogokariyan.com) · Masjid Kampus UGM · Masjid Nurul Ashri Deresan · MTA · pencarian |
| makassar | Makassar | Masjid Al-Markaz Al-Islami · Masjid Raya Makassar · pencarian "kajian rutin makassar" |

## 2. Aturan ekstraksi (KETAT — ini yang membedakan berguna dan berbahaya)
1. Hanya kajian **RUTIN MINGGUAN**: ada kata "setiap", "rutin", "tiap Ahad/Sabtu/…", "pekanan". Tabligh akbar, dauroh, atau acara bertanggal tunggal → JANGAN.
2. Wajib ada **hari (Senin..Ahad), jam mulai, nama masjid/lokasi**. Kurang satu → lewati.
3. **Jangan mengarang.** Jam selesai tidak disebut → kosong. Alamat tidak disebut → kosong. Pemateri tidak disebut → kosong.
4. "Ba'da Maghrib" tanpa angka → mulai `18:15`; "ba'da Isya" → `19:30`; "ba'da Subuh" → `05:00`; "ba'da Ashar" → `15:30`; "ba'da Dzuhur" → `12:30` — dan tulis frasa aslinya di deskripsi.
5. `terakhir_terlihat` = tanggal terbit halaman/post; kalau halaman jadwal resmi masjid tanpa tanggal → tanggal hari ini.
6. `confidence`: `tinggi` = halaman jadwal resmi masjid/lembaga ATAU ≥2 sumber sepakat; `sedang` = 1 agregator/berita/Telegram aktif; `rendah` = ragu rutin atau data lama (>12 bulan).
7. Kajian sama dari 2 sumber → 1 entri, dua URL di `sumber`.
8. **Jangan mengambil dari Instagram/Facebook** — robots.txt mereka melarang crawler, dan WebFetch akan menolak. Telegram publik lewat `t.me/s/<channel>` boleh.
9. Maksimal 30 entri per wilayah per hari; utamakan yang paling segar.

## 2b. AGENDA BERTANGGAL (tabligh akbar, dauroh, kajian tematik, kajian Ahad tertentu)
Selain kajian rutin, kumpulkan juga acara yang punya TANGGAL tertentu — ini yang paling sering diumumkan di Telegram (mis. t.me/s/markazilmuofficial, t.me/s/infokajianbandung, t.me/s/jadwalkajianID). Aturannya:
1. Wajib ada **tanggal Masehi lengkap** (hari + tanggal + bulan + tahun; kalau tahun tidak ditulis, pakai tahun yang membuat tanggalnya jatuh ≤ 90 hari ke depan), **jam mulai**, dan **nama masjid/tempat** (atau "Zoom"/"YouTube" untuk daring — set `online: true`).
2. Hanya acara **hari ini sampai 90 hari ke depan**. Acara yang sudah lewat → lewati (gabung.py juga membuangnya otomatis).
3. Sama seperti rutin: jangan mengarang alamat/pemateri/jam selesai; frasa "ba'da …" dikonversi sesuai aturan 2.4.
4. `confidence` `tinggi` = diumumkan penyelenggara/masjid sendiri (kanal resmi atau situs masjid); `sedang` = agregator/reposting; `rendah` = ragu.
5. Kalau ada tautan pendaftaran atau livestream, taruh di `tautan` (satu URL).
6. Maksimal 15 agenda per wilayah per hari, utamakan yang paling dekat tanggalnya.
7. Post yang sama diposting ulang → satu entri. Acara serial bertanggal (mis. "Ahad 4, 11, 18 Okt") → satu entri per tanggal.

## 3. Menulis hasil
Untuk tiap wilayah, tulis `hasil/<slug>.json`:
```json
{"kota":"Nama kota untuk ditampilkan","dicek":"YYYY-MM-DD","kajian":[
 {"judul":"…","pemateri":"…","lokasi":"…","alamat":"…","kota":"…","hari":1,"mulai":"HH:MM","selesai":"","kategori":"…","deskripsi":"≤1 kalimat, dari sumber","sumber":["https://…"],"terakhir_terlihat":"YYYY-MM-DD","confidence":"tinggi|sedang|rendah"}
]}
```
Tambahkan array `"agenda"` (boleh kosong `[]`) di berkas yang sama untuk acara bertanggal:
```json
{"kota":"…","dicek":"YYYY-MM-DD","kajian":[…],"agenda":[
 {"judul":"…","pemateri":"…","lokasi":"…","alamat":"…","kota":"…","tanggal":"YYYY-MM-DD","mulai":"HH:MM","selesai":"","kategori":"Tabligh Akbar|Dauroh|Kajian Tematik|Kajian Online|…","deskripsi":"≤1 kalimat, dari sumber","online":false,"tautan":"","sumber":["https://…"],"terakhir_terlihat":"YYYY-MM-DD","confidence":"tinggi|sedang|rendah"}
]}
```
`kota` yang ditampilkan: "Bandung", "Jakarta Selatan", "Jakarta Pusat", "Jakarta Utara", "Jakarta Timur", "Jakarta Barat", "Bogor", "Depok", "Tangerang", "Bekasi", "Surabaya", "Yogyakarta", "Makassar" (tulis per kota, bukan gabungan).

Lalu:
```
python3 gabung.py            # menggabung ke kajian.json, dedupe, kadaluarsa 24 bulan
python3 -c "import json;json.load(open('kajian.json'))"   # harus valid
git add -A && git commit -m "crawl: <slug1>, <slug2> — <N> entri" && git push
```
`gabung.py` TIDAK menghapus entri wilayah lain dan tidak menghapus entri rutin lama yang tidak kamu temukan lagi (baru kadaluarsa setelah 24 bulan) — jadi hasil kosong tidak merusak apa pun. Agenda bertanggal dibuang otomatis sehari setelah tanggalnya lewat.

## 4. Kalau gagal
- Sumber gagal → lanjut ke sumber lain, catat di laporan.
- `git push` ditolak → `git pull --rebase` lalu push lagi, sekali.
- Kalau tetap gagal, jangan mengulang tanpa batas: tulis laporan dan berhenti.

## 5. Laporan akhir (ringkas, Bahasa Indonesia)
Wilayah yang dikerjakan · entri rutin baru / diperbarui / total · agenda bertanggal baru / total · sumber yang mati · hal yang mencurigakan (mis. dua sumber beda jam untuk kajian yang sama).
