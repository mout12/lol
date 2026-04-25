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

HTTP API:
  name: lol-admin-api
  id: gil40t7dfi
  endpoint: https://gil40t7dfi.execute-api.us-east-2.amazonaws.com

Protected route:
  POST /current

Lambda integration:
  function: lol-update-current-json
```

## Behavior

`POST /current` requires a Cognito bearer token and accepts:

```json
{
  "url": "https://example.com"
}
```

The route calls `lol-update-current-json`, which validates the URL and overwrites `s3://lol-buck-mx/current.json`.

Unauthenticated requests return `401 Unauthorized`.

## Current Limits

- No real admin user has been created yet.
- CORS currently allows all origins for the prototype API. Tighten this to the admin site origin when `admin.lol.buck.mx` exists.
- The API only supports setting the current URL. URL history/list support still needs storage and routes.
