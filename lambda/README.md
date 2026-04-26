# current.json writer Lambda

This Lambda updates `s3://lol-buck-mx/current.json` and maintains `s3://lol-buck-mx/history.json`.

It expects an event shaped like:

```json
{
  "url": "https://example.com",
  "description": "Optional display label"
}
```

The function validates that the URL uses `http://` or `https://`, then writes:

```json
{
  "url": "https://example.com"
}
```

It also records the URL in `history.json`, de-duplicated by URL with the most recently selected item first. `description` is optional and is used by the admin UI as the history display label.

The deployed function is intended to be the write path behind the future admin UI. The public redirect page still reads `current.json`.
