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

Unauthenticated requests return `401 Unauthorized`.

Browser calls are allowed only from:

```text
https://admin.lol.buck.mx
```

## Current Limits

- The real admin user exists, but still needs to complete first login and set a permanent password through `admin.html`.
- `admin.html` can now set the active redirect URL through the protected `POST /current` endpoint.
- GitHub Actions no longer uploads `current.json`; the admin page/API are now the management path for active redirect state.
