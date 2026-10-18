"""Import validated sample records: python -m scripts.seed."""

import json

from app.config import ROOT_DIR, get_db
from app.models import DataItemCreate


def main():
    records = json.loads(
        (ROOT_DIR / "seed_data.json").read_text(encoding="utf-8")
    )
    items = [DataItemCreate.model_validate(item) for item in records]
    db = get_db()
    batch = db.batch()
    for index, item in enumerate(items):
        # Stable IDs make repeated imports overwrite only these sample records.
        doc = db.collection("data").document(f"sample-{index:03d}")
        batch.set(doc, item.model_dump(mode="json"))
    batch.commit()
    print(f"Imported {len(items)} sample learning records")


if __name__ == "__main__":
    main()
