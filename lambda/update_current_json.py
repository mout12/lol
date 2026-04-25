import json
import os
from urllib.parse import urlparse

import boto3


s3 = boto3.client("s3")


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


def handler(event, context):
    try:
        payload = _event_payload(event)
        url = _validate_url(payload.get("url"))
    except (json.JSONDecodeError, ValueError) as exc:
        return _response(400, {"error": str(exc)})

    bucket = os.environ["REDIRECT_BUCKET"]
    key = os.environ.get("REDIRECT_KEY", "current.json")
    body = json.dumps({"url": url}, indent=2) + "\n"

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-store, no-cache, must-revalidate, max-age=0",
    )

    return _response(200, {"url": url})
