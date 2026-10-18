"""Load settings and initialize Firestore only when a request needs it."""

import json
import os
from functools import lru_cache
from pathlib import Path

import firebase_admin
from dotenv import load_dotenv
from fastapi import HTTPException
from firebase_admin import credentials, firestore

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@lru_cache
def get_db():
    """Reuse Firebase; return 503 when local credentials are missing."""
    try:
        try:
            firebase_admin.get_app()
        except ValueError:
            account = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
            key_path = Path(
                os.getenv(
                    "GOOGLE_APPLICATION_CREDENTIALS",
                    str(ROOT_DIR / "serviceAccountKey.json"),
                )
            )
            if account:
                credential = credentials.Certificate(json.loads(account))
            elif key_path.is_file():
                credential = credentials.Certificate(str(key_path))
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Firebase credentials are not configured",
                )
            firebase_admin.initialize_app(credential)
        return firestore.client()
    except HTTPException:
        raise
    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=503, detail="Firebase configuration is invalid"
        ) from exc
