# Admin API

The admin write path is currently an AWS HTTP API protected by a Cognito JWT authorizer.

## AWS Resources

```text
Region: us-east-2

Cognito user pool:
  name: lol-admin-users
  id: us-east-2_J0l6jb3qZ

Cognito app client:
  name: lol-admin-web
  id: mjj7ggl6ti48cu6s8qutdek1k

Cognito admin user:
  email: <admin-email>
  status: FORCE_CHANGE_PASSWORD until first login

HTTP API:
  name: lol-admin-api
  id: gil40t7dfi
  endpoint: https://gil40t7dfi.execute-api.us-east-2.amazonaws.com

Protected route:
  POST /current

Lambda integration:
  function: lol-update-current-json

Admin login page:
  object: s3://lol-buck-mx/admin.html

Admin-managed redirect state:
  current: s3://lol-buck-mx/current.json
  history: s3://lol-buck-mx/history.json
```

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

Unauthenticated requests return `401 Unauthorized`.

## Current Limits

- The real admin user exists, but still needs to complete first login and set a permanent password through `admin.html`.
- `admin.html` can now set the active redirect URL through the protected `POST /current` endpoint.
- CORS currently allows all origins for the prototype API. Tighten this to the admin site origin when `admin.lol.buck.mx` exists.
- GitHub Actions no longer uploads `current.json`; the admin page/API are now the management path for active redirect state.
