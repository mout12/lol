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

To delete a history item without changing `current.json`, send:

```json
{
  "action": "delete",
  "url": "https://example.com"
}
```

To upload a photo from the admin page, first request a presigned upload:

```json
{
  "action": "createPhotoUpload",
  "fileName": "photo.jpg",
  "contentType": "image/jpeg"
}
```

The function returns an S3 `PUT` URL and the final public URL for the uploaded object. After the browser uploads the file directly to S3, it sends the returned public URL back through the normal redirect update path with the same optional `description` field.

The deployed Lambda role needs `s3:PutObject` for `arn:aws:s3:::lol-buck-mx/uploads/*` to create presigned upload URLs. The S3 bucket also needs CORS allowing `PUT` from `https://admin.lol.buck.mx`.

The public redirect page still reads `current.json`.
