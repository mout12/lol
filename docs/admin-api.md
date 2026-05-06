# Admin API

The admin write path is currently an AWS HTTP API protected by a Cognito JWT authorizer.

## AWS Resources

```text
Region: us-east-2

Cognito user pool:
  name: lol-admin-users
  id: <cognito-user-pool-id>

Cognito app client:
  name: lol-admin-web
  id: <cognito-app-client-id>

Cognito admin user:
  email: <admin-email>
  status: FORCE_CHANGE_PASSWORD until first login

HTTP API:
  name: lol-admin-api
  id: <admin-api-id>
  endpoint: <admin-api-endpoint>
  CORS allow origin: https://admin.lol.buck.mx

Protected route:
  POST /current

Lambda integration:
  function: lol-update-current-json

Admin login page:
  URL: https://admin.lol.buck.mx
  object: s3://lol-buck-mx/admin.html

Admin HTTPS hosting:
  CloudFront distribution: <cloudfront-distribution-id>
  CloudFront domain: <cloudfront-domain>
  ACM certificate: arn:aws:acm:us-east-1:<account-id>:certificate/<certificate-id>
  GoDaddy CNAME: admin.lol -> <cloudfront-domain>
  GoDaddy ACM validation CNAME: <acm-validation-cname-name> -> <acm-validation-cname-value>

Admin-managed redirect state:
  current: s3://lol-buck-mx/current.json
  history: s3://lol-buck-mx/history.json

Admin photo uploads:
  prefix: s3://lol-buck-mx/uploads/
  public URL base: https://admin.lol.buck.mx/uploads/
```

The redirect state file contract is documented in [`redirect-state.md`](redirect-state.md).

## Behavior

`POST /current` requires a Cognito bearer token and accepts:

```json
{
  "url": "https://example.com",
  "description": "Optional history label"
}
```

The route calls `lol-update-current-json`, which validates the URL and overwrites `s3://lol-buck-mx/current.json`.
It also updates `s3://lol-buck-mx/history.json` with a de-duplicated list of prior selected URLs and optional descriptions.

The same route accepts:

```json
{
  "action": "delete",
  "url": "https://example.com"
}
```

for removing a URL from history without changing `current.json`.

The route also accepts:

```json
{
  "action": "createPhotoUpload",
  "fileName": "photo.jpg",
  "contentType": "image/jpeg"
}
```

for creating a short-lived presigned S3 upload URL. The admin page uploads the image file directly to S3, then submits the uploaded photo URL back through the normal redirect update path with the same optional `description` field.

Unauthenticated requests return `401 Unauthorized`.

Browser calls are allowed only from:

```text
https://admin.lol.buck.mx
```

## Current Limits

- The real admin user exists, but still needs to complete first login and set a permanent password through `admin.html`.
- `admin.html` can now set the active redirect URL through the protected `POST /current` endpoint.
- `admin.html` can request a presigned photo upload, upload the selected image to `uploads/`, and set the uploaded photo URL as the active redirect.
- GitHub Actions no longer uploads `current.json`; the admin page/API are now the management path for active redirect state.

## Photo Upload Deployment Notes

The deployed Lambda role needs `s3:PutObject` on:

```text
arn:aws:s3:::lol-buck-mx/uploads/*
```

The S3 bucket CORS configuration must allow browser `PUT` uploads from:

```text
https://admin.lol.buck.mx
```

with at least the `Content-Type` and `Cache-Control` request headers allowed. The Lambda can set `PHOTO_PUBLIC_BASE_URL` to override the default public URL base of `https://admin.lol.buck.mx`.
