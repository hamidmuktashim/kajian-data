#!/usr/bin/env python3
"""Gabungkan hasil crawl per wilayah (hasil/*.json) ke kajian.json.
Aturan: id stabil dari judul|lokasi|hari|mulai; entri lama dipertahankan sampai
24 bulan tidak terlihat; hasil baru memperbarui jam/pemateri/sumber; konflik → yang terbaru menang.
Agenda bertanggal (hasil/*.json → "agenda") digabung terpisah: id dari judul|lokasi|tanggal|mulai, dibuang H+1 setelah tanggalnya."""
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

def tgl(v):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", str(v or ""))
    if not m: return ""
    try: return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
    except ValueError: return ""
def aid(a):
    t = "|".join([norm(a["judul"]).lower(), norm(a["lokasi"]).lower(), a["tanggal"], a["mulai"]])
    return "ag_" + hashlib.sha1(t.encode()).hexdigest()[:10]
def bersih_agenda(r, kota_default=""):
    """Acara bertanggal (tabligh akbar, dauroh, kajian tematik). Wajib: judul, lokasi, tanggal, mulai."""
    a = {"judul": norm(r.get("judul")), "pemateri": norm(r.get("pemateri")), "lokasi": norm(r.get("lokasi")),
         "alamat": norm(r.get("alamat")), "kota": norm(r.get("kota")) or kota_default, "tanggal": tgl(r.get("tanggal")),
         "mulai": jam(r.get("mulai")), "selesai": jam(r.get("selesai")), "kategori": norm(r.get("kategori")) or "Agenda",
         "deskripsi": norm(r.get("deskripsi"))[:240], "online": bool(r.get("online")),
         "tautan": norm(r.get("tautan")) if str(r.get("tautan") or "").startswith("http") else "",
         "sumber": [s for s in (r.get("sumber") or []) if isinstance(s, str) and s.startswith("http")][:4],
         "terakhir_terlihat": norm(r.get("terakhir_terlihat"))[:10], "confidence": norm(r.get("confidence")) or "sedang"}
    if not (a["judul"] and a["lokasi"] and a["tanggal"] and a["mulai"]): return None
    if a["confidence"] not in ("tinggi", "sedang", "rendah"): a["confidence"] = "sedang"
    a["id"] = aid(a); return a

def main():
    today = datetime.date.today()
    lama, lama_ag = {}, {}
    if os.path.exists(OUT):
        _d = json.load(open(OUT, encoding="utf-8"))
        for k in _d.get("kajian", []): lama[k["id"]] = k
        for a in _d.get("agenda", []): lama_ag[a["id"]] = a
    baru, baru_ag = {}, {}
    for f in sorted(glob.glob(os.path.join(ROOT, "hasil", "*.json"))):
        try: d = json.load(open(f, encoding="utf-8"))
        except Exception as e: print("lewati", f, e); continue
        for r in d.get("agenda", []) or []:
            a = bersih_agenda(r, d.get("kota", ""))
            if not a: continue
            if a["id"] in baru_ag:
                b = baru_ag[a["id"]]; b["sumber"] = list(dict.fromkeys(b["sumber"] + a["sumber"]))[:4]
                if len(b["sumber"]) >= 2 and b["confidence"] != "tinggi": b["confidence"] = "tinggi"
            else: baru_ag[a["id"]] = a
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
    # agenda bertanggal: entri lama dipertahankan, entri baru menimpa field yang terisi; buang yang sudah lewat (H+1)
    ag = dict(lama_ag)
    for i, a in baru_ag.items():
        if i in ag:
            g = ag[i]; g.update({x: a[x] for x in ("pemateri", "selesai", "kategori", "deskripsi", "alamat", "tautan") if a[x]})
            g["sumber"] = list(dict.fromkeys(a["sumber"] + g.get("sumber", [])))[:4]
            g["terakhir_terlihat"] = max(g.get("terakhir_terlihat", ""), a["terakhir_terlihat"])
            g["confidence"] = a["confidence"] if a["confidence"] != "rendah" else g.get("confidence", "rendah")
            g["online"] = a["online"] or g.get("online", False)
        else:
            a["pertama_terlihat"] = today.isoformat(); ag[i] = a
    kemarin = (today - datetime.timedelta(days=1)).isoformat()
    agenda = [a for a in ag.values() if a.get("tanggal", "") >= kemarin]
    agenda.sort(key=lambda a: (a["tanggal"], a["mulai"], a["kota"]))
    kota = sorted({k["kota"] for k in hasil} | {a["kota"] for a in agenda})
    json.dump({"versi": 2, "diperbarui": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="minutes"),
               "kota": kota, "jumlah": len(hasil), "jumlah_agenda": len(agenda), "kajian": hasil, "agenda": agenda},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"kajian.json: {len(hasil)} rutin ({len(baru)} dari hasil baru, {len(hasil)-len(lama) if lama else len(hasil)} bertambah); "
          f"{len(agenda)} agenda bertanggal ({len(baru_ag)} dari hasil baru, {len(ag)-len(agenda)} dibuang karena lewat); kota: {', '.join(kota)}")

if __name__ == "__main__": main()
