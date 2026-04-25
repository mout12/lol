# current.json writer Lambda

This Lambda updates `s3://lol-buck-mx/current.json`.

It expects an event shaped like:

```json
{
  "url": "https://example.com"
}
```

The function validates that the URL uses `http://` or `https://`, then writes:

```json
{
  "url": "https://example.com"
}
```

The deployed function is intended to be the write path behind the future admin UI. The public redirect page still reads `current.json`.
