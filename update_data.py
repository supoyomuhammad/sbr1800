"""
update_data.py — Generate ulang data.json dari file data mentah
================================================================
Cara pakai:
  1. Ganti file  raw_data.json  dengan data terbaru (hasil export dari sistem)
  2. Jalankan:   python update_data.py
  3. File  data.json  otomatis terupdate
  4. Commit & push ke GitHub → Netlify otomatis deploy

Tidak perlu install library apapun, cukup Python 3.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

RAW_FILE  = "raw_data.json"   # file mentah dari sistem (array of records)
OUT_FILE  = "data.json"       # output yang dibaca dashboard


def generate():
    raw_path = Path(RAW_FILE)
    if not raw_path.exists():
        print(f"❌  File '{RAW_FILE}' tidak ditemukan.")
        return

    with open(raw_path, encoding="utf-8") as f:
        data = json.load(f)

    print(f"📥  Membaca {len(data):,} record dari '{RAW_FILE}'...")

    # ── Agregasi per kabupaten ────────────────────────────────
    kab_dates = defaultdict(list)
    for d in data:
        kab_dates[d["kabupaten_kota"]].append(d["created_at"][:10])

    kabupaten_list = []
    for kab, dates in sorted(kab_dates.items()):
        day_counts = Counter(dates)
        kabupaten_list.append({
            "nama":   kab,
            "total":  len(dates),
            "harian": dict(sorted(day_counts.items()))
        })
    kabupaten_list.sort(key=lambda x: -x["total"])

    # ── Agregasi per user ─────────────────────────────────────
    user_kab = defaultdict(lambda: defaultdict(int))
    for d in data:
        user_kab[d["username"]][d["kabupaten_kota"]] += 1

    user_total = Counter(d["username"] for d in data)
    users_list = []
    for username, total in user_total.most_common():
        users_list.append({
            "username":  username,
            "total":     total,
            "kabupaten": dict(sorted(user_kab[username].items(), key=lambda x: -x[1]))
        })

    # ── Build summary ─────────────────────────────────────────
    last_updated = max(d["created_at"] for d in data)[:16]
    summary = {
        "kabupaten":     kabupaten_list,
        "users":         users_list,
        "total_records": len(data),
        "last_updated":  last_updated
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"✅  '{OUT_FILE}' berhasil di-generate!")
    print(f"    📊  {len(data):,} usaha  |  {len(kabupaten_list)} kab/kota  |  {len(users_list)} petugas")
    print(f"    🕐  Data terakhir: {last_updated}")
    print(f"\n    Selanjutnya: git add data.json && git commit -m 'update data' && git push")


if __name__ == "__main__":
    generate()
