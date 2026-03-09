from __future__ import annotations

import json
from pathlib import Path

from app.db import connect


BUILTIN_VOICES = [
    {"id": "alba", "name": "alba", "type": "builtin", "language": "en"},
    {"id": "sol", "name": "sol", "type": "builtin", "language": "en"},
]


class VoiceRegistry:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def list_all(self) -> list[dict]:
        result = list(BUILTIN_VOICES)
        with connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM voices ORDER BY created_at DESC").fetchall()
        for row in rows:
            result.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "type": row["type"],
                    "language": row["language"] or "en",
                    "sample_path": row["sample_path"],
                    "embedding_path": row["embedding_path"],
                    "metadata": json.loads(row["metadata_json"] or "{}"),
                }
            )
        return result

    def get(self, voice_id: str) -> dict | None:
        if voice_id in {v["id"] for v in BUILTIN_VOICES}:
            return next(v for v in BUILTIN_VOICES if v["id"] == voice_id)
        with connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM voices WHERE id = ?", (voice_id,)).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "name": row["name"],
            "type": row["type"],
            "language": row["language"] or "en",
            "sample_path": row["sample_path"],
            "embedding_path": row["embedding_path"],
            "metadata": json.loads(row["metadata_json"] or "{}"),
        }

    def create_cloned(self, voice_id: str, name: str, sample_path: str, embedding_path: str | None = None, metadata: dict | None = None) -> dict:
        metadata = metadata or {}
        with connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO voices (id, name, type, language, sample_path, embedding_path, metadata_json) VALUES (?, ?, 'cloned', 'en', ?, ?, ?)",
                (voice_id, name, sample_path, embedding_path, json.dumps(metadata)),
            )
            conn.commit()
        return self.get(voice_id)

    def update(self, voice_id: str, *, name: str | None = None, metadata: dict | None = None) -> dict:
        current = self.get(voice_id)
        if not current or current.get("type") != "cloned":
            raise ValueError("Only cloned voices can be updated")
        new_name = name or current["name"]
        new_metadata = metadata if metadata is not None else current.get("metadata", {})
        with connect(self.db_path) as conn:
            conn.execute("UPDATE voices SET name = ?, metadata_json = ? WHERE id = ?", (new_name, json.dumps(new_metadata), voice_id))
            conn.commit()
        return self.get(voice_id)

    def delete(self, voice_id: str) -> dict:
        current = self.get(voice_id)
        if not current or current.get("type") != "cloned":
            raise ValueError("Only cloned voices can be deleted")
        with connect(self.db_path) as conn:
            conn.execute("DELETE FROM voices WHERE id = ?", (voice_id,))
            conn.commit()
        return current
