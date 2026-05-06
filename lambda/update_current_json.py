import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError


s3 = boto3.client("s3")

MAX_ORIGINAL_FILENAME_LENGTH = 80
PRESIGNED_UPLOAD_EXPIRES_SECONDS = 300


def _response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Cache-Control": "no-store",
        },
        "body": json.dumps(payload),
    }


def _event_payload(event):
    if isinstance(event, dict) and isinstance(event.get("body"), str):
        return json.loads(event["body"] or "{}")

    return event if isinstance(event, dict) else {}


def _validate_url(value):
    if not isinstance(value, str):
        raise ValueError("url must be a string")

    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("url must start with http:// or https://")

    return value


def _action_payload(payload):
    action = payload.get("action", "set")
    if action not in ("set", "delete", "createPhotoUpload"):
        raise ValueError("action must be set, delete, or createPhotoUpload")

    return action


def _photo_upload_payload(payload):
    content_type = payload.get("contentType")
    original_filename = payload.get("fileName", "photo")

    if not isinstance(content_type, str) or not content_type.startswith("image/"):
        raise ValueError("contentType must be an image MIME type")

    if not isinstance(original_filename, str):
        raise ValueError("fileName must be a string")

    safe_filename = re.sub(r"[^A-Za-z0-9._-]+", "-", original_filename.strip())
    safe_filename = safe_filename.strip(".-")[:MAX_ORIGINAL_FILENAME_LENGTH] or "photo"
    now = datetime.now(timezone.utc)
    key = (
        f"uploads/{now:%Y/%m/%d}/"
        f"{now:%Y%m%dT%H%M%SZ}-{safe_filename}"
    )

    return key, content_type


def _description_payload(payload):
    if "description" not in payload:
        return False, None

    value = payload.get("description")
    if value is None:
        return True, ""

    if not isinstance(value, str):
        raise ValueError("description must be a string")

    return True, value.strip()


def _read_history(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") in ("NoSuchKey", "404", "AccessDenied"):
            return []
        raise

    data = json.loads(response["Body"].read().decode("utf-8"))
    urls = data.get("urls", [])
    return urls if isinstance(urls, list) else []


def _write_json(bucket, key, payload):
    body = json.dumps(payload, indent=2) + "\n"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-store, no-cache, must-revalidate, max-age=0",
    )


def _updated_history(existing_history, url, description_was_provided, description):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    existing_item = next(
        (
            item
            for item in existing_history
            if isinstance(item, dict) and item.get("url") == url
        ),
        {},
    )
    existing_description = existing_item.get("description", "")
    next_description = description if description_was_provided else existing_description
    next_item = {"url": url, "updatedAt": now}

    if next_description:
        next_item["description"] = next_description

    history = [
        item
        for item in existing_history
        if isinstance(item, dict) and item.get("url") != url
    ]
    history.insert(0, next_item)
    return history[:25]


def _deleted_history(existing_history, url):
    return [
        item
        for item in existing_history
        if isinstance(item, dict) and item.get("url") != url
    ]


def handler(event, context):
    try:
        payload = _event_payload(event)
        action = _action_payload(payload)
        url = None if action == "createPhotoUpload" else _validate_url(payload.get("url"))
        description_was_provided, description = _description_payload(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        return _response(400, {"error": str(exc)})

    bucket = os.environ["REDIRECT_BUCKET"]
    current_key = os.environ.get("REDIRECT_KEY", "current.json")
    history_key = os.environ.get("HISTORY_KEY", "history.json")
    photo_public_base_url = os.environ.get(
        "PHOTO_PUBLIC_BASE_URL", "https://admin.lol.buck.mx"
    ).rstrip("/")

    if action == "createPhotoUpload":
        try:
            key, content_type = _photo_upload_payload(payload)
            cache_control = "public, max-age=31536000, immutable"
            upload_url = s3.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": bucket,
                    "Key": key,
                    "ContentType": content_type,
                    "CacheControl": cache_control,
                },
                ExpiresIn=PRESIGNED_UPLOAD_EXPIRES_SECONDS,
            )
        except ValueError as exc:
            return _response(400, {"error": str(exc)})

        return _response(
            200,
            {
                "key": key,
                "url": f"{photo_public_base_url}/{key}",
                "uploadUrl": upload_url,
                "uploadHeaders": {
                    "Content-Type": content_type,
                    "Cache-Control": cache_control,
                },
                "expiresIn": PRESIGNED_UPLOAD_EXPIRES_SECONDS,
            },
        )

    existing_history = _read_history(bucket, history_key)

    if action == "delete":
        history = _deleted_history(existing_history, url)
        _write_json(bucket, history_key, {"urls": history})
        return _response(200, {"url": url, "history": history, "deleted": True})

    history = _updated_history(existing_history, url, description_was_provided, description)

    _write_json(bucket, current_key, {"url": url})
    _write_json(bucket, history_key, {"urls": history})

    return _response(200, {"url": url, "history": history})
