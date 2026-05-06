# Redirect State

The active redirect target is stored outside the Git repository in S3:

```text
s3://lol-buck-mx/current.json
```

The public redirect page reads `./current.json` at request time. The admin API is the write path for that object.

## current.json

Required shape:

```json
{
  "url": "https://example.com"
}
```

Rules:

- The file must be valid JSON.
- The top-level value must be an object.
- `url` must be a string.
- `url` must start with `http://` or `https://`.

## history.json

The admin page also reads prior redirect targets from:

```text
s3://lol-buck-mx/history.json
```

Expected shape:

```json
{
  "urls": [
    {
      "url": "https://example.com",
      "description": "Optional display label",
      "updatedAt": "2026-04-26T21:42:00+00:00"
    }
  ]
}
```

Rules:

- `urls` should be an array.
- Each item should include a `url` string.
- `description` is optional.
- `updatedAt` is written by the Lambda and is used for display/context only.

## Uploaded Photos

Photo uploads use the same redirect state contract. Uploaded image objects are stored under:

```text
s3://lol-buck-mx/uploads/
```

After upload, the active `current.json` URL is set to the public URL for that uploaded object, and the optional admin description is stored in `history.json` like any other redirect target.
