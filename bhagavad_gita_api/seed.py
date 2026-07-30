import requests
import time
from sqlalchemy.orm import Session

from bhagavad_gita_api.db.session import SessionLocal
from bhagavad_gita_api.models import gita as models

BASE = "https://bhagavadgita.io/api/v2"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def safe_get(url, retries=3):
    for i in range(retries):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)

            if res.status_code != 200:
                print(f"❌ Failed {res.status_code} → {url}")
                print(res.text[:200])
                time.sleep(2)
                continue

            try:
                return res.json()
            except Exception:
                print(f"❌ Not JSON → {url}")
                print(res.text[:200])
                time.sleep(2)

        except Exception as e:
            print(f"⚠️ Error: {e} → retry {i+1}")
            time.sleep(2)

    return None


def main():
    db: Session = SessionLocal()

    print("🚀 Seeding database...")

    chapters = safe_get(f"{BASE}/chapters")
    if not chapters:
        print("❌ Failed to fetch chapters. Exiting.")
        return

    for ch in chapters:
        ch_num = ch["chapter_number"]
        print(f"📘 Chapter {ch_num}")

        # Insert chapter
        chapter = models.GitaChapter(
            id=ch["id"],
            chapter_number=ch["chapter_number"],
            name=ch["name"],
            name_translated=ch.get("name_translated"),
            name_transliterated=ch.get("name_transliterated"),
            verses_count=ch.get("verses_count"),
            chapter_summary=ch.get("chapter_summary"),
        )
        db.merge(chapter)

        # Fetch verses
        verses = safe_get(f"{BASE}/chapters/{ch_num}/verses")
        if not verses:
            print(f"⚠️ Skipping Chapter {ch_num} (no verses)")
            continue

        for v in verses:
            verse = models.GitaVerse(
                id=v["id"],
                chapter_number=v["chapter_number"],
                verse_number=v["verse_number"],
                text=v.get("text"),
                transliteration=v.get("transliteration"),
            )
            db.merge(verse)

        db.commit()
        time.sleep(0.5)  # avoid rate limit

    db.close()
    print("✅ Seeding complete")


if __name__ == "__main__":
    main()