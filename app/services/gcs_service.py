"""
Google Cloud Storage Service
Stores BRDs and uploaded files in GCS.
Falls back to /tmp file storage when GCS credentials are unavailable (e.g. HF Spaces free tier).
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# File-based fallback storage directory (works on HF Spaces /tmp)
_LOCAL_STORE = Path("/tmp/brd_sessions")
_LOCAL_STORE.mkdir(parents=True, exist_ok=True)


def _local_save(session_id: str, brd_data: dict) -> str:
    """Save BRD to local /tmp file and return path."""
    path = _LOCAL_STORE / f"{session_id}.json"
    path.write_text(json.dumps(brd_data, indent=2), encoding="utf-8")
    return str(path)


def _local_load(session_id: str) -> Optional[dict]:
    """Load BRD from local /tmp file."""
    path = _LOCAL_STORE / f"{session_id}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None

# Lazy import so app works without GCS creds during dev
_gcs_client = None


def _get_client():
    global _gcs_client
    if _gcs_client is None:
        try:
            from google.cloud import storage
            _gcs_client = storage.Client()
        except Exception:
            return None
    return _gcs_client


BUCKET_NAME = os.environ.get("GCS_BUCKET", "autoresearch-ai-brd-store")


async def upload_brd(session_id: str, brd_data: dict) -> Optional[str]:
    """Upload generated BRD JSON to GCS. Falls back to /tmp on failure."""
    # Always save locally first as a reliable fallback
    local_path = _local_save(session_id, brd_data)
    print(f"[Storage] Saved BRD locally: {local_path}")

    client = _get_client()
    if not client:
        print("[GCS] No client - using local fallback only")
        return f"local://{local_path}"

    try:
        bucket = client.bucket(BUCKET_NAME)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        blob_name = f"brds/{session_id}/{timestamp}_brd.json"
        blob = bucket.blob(blob_name)

        blob.upload_from_string(
            json.dumps(brd_data, indent=2),
            content_type="application/json"
        )
        uri = f"gs://{BUCKET_NAME}/{blob_name}"
        print(f"[GCS] Uploaded BRD: {uri}")
        return uri

    except Exception as e:
        print(f"[GCS] Upload failed: {e} — local fallback already saved")
        return f"local://{local_path}"


async def upload_file(session_id: str, filename: str, file_bytes: bytes, mime_type: str) -> Optional[str]:
    """Upload raw input file to GCS for audit trail."""
    client = _get_client()
    if not client:
        return None

    try:
        bucket = client.bucket(BUCKET_NAME)
        blob_name = f"inputs/{session_id}/{filename}"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(file_bytes, content_type=mime_type)
        return f"gs://{BUCKET_NAME}/{blob_name}"
    except Exception as e:
        print(f"[GCS] File upload failed: {e}")
        return None


async def get_brd(session_id: str) -> Optional[dict]:
    """Retrieve BRD — tries GCS first, then local /tmp fallback."""
    # Try GCS first
    client = _get_client()
    if client:
        try:
            bucket = client.bucket(BUCKET_NAME)
            blobs = list(client.list_blobs(BUCKET_NAME, prefix=f"brds/{session_id}/"))
            if blobs:
                latest = sorted(blobs, key=lambda b: b.name)[-1]
                return json.loads(latest.download_as_text())
        except Exception as e:
            print(f"[GCS] Get BRD failed: {e} — trying local fallback")

    # Fall back to local /tmp storage
    local_brd = _local_load(session_id)
    if local_brd:
        print(f"[Storage] Loaded BRD from local fallback for session {session_id}")
    return local_brd
