#!/usr/bin/env python3
"""Gabungkan hasil crawl per wilayah (hasil/*.json) ke kajian.json.
Aturan: id stabil dari judul|lokasi|hari|mulai; entri lama dipertahankan sampai
24 bulan tidak terlihat; hasil baru memperbarui jam/pemateri/sumber; konflik → yang terbaru menang."""
import json, glob, os, re, sys, datetime, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, "kajian.json")
HARI = ["", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad"]
KADALUARSA_BULAN = 24

def norm(s): return re.sub(r"\s+", " ", str(s or "")).strip()
def jam(v):
    m = re.search(r"(\d{1,2})[.:](\d{2})", str(v or ""))
    return f"{int(m.group(1)):02d}:{m.group(2)}" if m else ""
def kid(k):
    t = "|".join([norm(k["judul"]).lower(), norm(k["lokasi"]).lower(), str(k["hari"]), k["mulai"]])
    return "kj_" + hashlib.sha1(t.encode()).hexdigest()[:10]
def bersih(r, kota_default=""):
    hari = int(str(r.get("hari") or 0)) if str(r.get("hari") or "").isdigit() else 0
    k = {"judul": norm(r.get("judul")), "pemateri": norm(r.get("pemateri")), "lokasi": norm(r.get("lokasi")),
         "alamat": norm(r.get("alamat")), "kota": norm(r.get("kota")) or kota_default, "hari": hari,
         "mulai": jam(r.get("mulai")), "selesai": jam(r.get("selesai")), "kategori": norm(r.get("kategori")) or "Kajian",
         "deskripsi": norm(r.get("deskripsi"))[:240],
         "sumber": [s for s in (r.get("sumber") or []) if isinstance(s, str) and s.startswith("http")][:4],
         "terakhir_terlihat": norm(r.get("terakhir_terlihat"))[:10], "confidence": norm(r.get("confidence")) or "sedang"}
    if not (k["judul"] and k["lokasi"] and 1 <= hari <= 7 and k["mulai"]): return None
    if k["confidence"] not in ("tinggi", "sedang", "rendah"): k["confidence"] = "sedang"
    k["id"] = kid(k); return k

def main():
    today = datetime.date.today()
    lama = {}
    if os.path.exists(OUT):
        for k in json.load(open(OUT, encoding="utf-8")).get("kajian", []): lama[k["id"]] = k
    baru = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "hasil", "*.json"))):
        try: d = json.load(open(f, encoding="utf-8"))
        except Exception as e: print("lewati", f, e); continue
        for r in d.get("kajian", []):
            k = bersih(r, d.get("kota", "")); 
            if not k: continue
            if k["id"] in baru:  # gabung sumber
                b = baru[k["id"]]; b["sumber"] = list(dict.fromkeys(b["sumber"] + k["sumber"]))[:4]
                if len(b["sumber"]) >= 2 and b["confidence"] != "tinggi": b["confidence"] = "tinggi"
                if k["terakhir_terlihat"] > b["terakhir_terlihat"]: b["terakhir_terlihat"] = k["terakhir_terlihat"]
            else: baru[k["id"]] = k
    gabung = dict(lama)
    for i, k in baru.items():
        if i in gabung:
            g = gabung[i]; g.update({x: k[x] for x in ("pemateri", "selesai", "kategori", "deskripsi", "alamat") if k[x]})
            g["sumber"] = list(dict.fromkeys(k["sumber"] + g.get("sumber", [])))[:4]
            g["terakhir_terlihat"] = max(g.get("terakhir_terlihat", ""), k["terakhir_terlihat"])
            g["confidence"] = k["confidence"] if k["confidence"] != "rendah" else g.get("confidence", "rendah")
        else:
            k["pertama_terlihat"] = today.isoformat(); gabung[i] = k
    # kadaluarsa
    batas = (today - datetime.timedelta(days=30 * KADALUARSA_BULAN)).isoformat()
    hasil = [k for k in gabung.values() if not k.get("terakhir_terlihat") or k["terakhir_terlihat"] >= batas]
    hasil.sort(key=lambda k: (k["kota"], k["hari"], k["mulai"]))
    kota = sorted({k["kota"] for k in hasil})
    json.dump({"versi": 1, "diperbarui": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="minutes"),
               "kota": kota, "jumlah": len(hasil), "kajian": hasil}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"kajian.json: {len(hasil)} entri, {len(baru)} dari hasil baru, {len(hasil)-len(lama) if lama else len(hasil)} bertambah; kota: {', '.join(kota)}")

if __name__ == "__main__": main()
