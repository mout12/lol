# AI Session Log

This file is an ongoing log of AI-assisted work on this repository.

When continuing work in a future AI session:

- Read this file first to understand the current project setup.
- Add a new dated entry at the top of the "Sessions" section.
- Keep entries factual: what changed, why it changed, security notes, and follow-up risks.
- Do not include secrets, tokens, passwords, or full temporary authentication codes.

## Project Snapshot

- Local path: `~/Projects/lol`
- GitHub repo: `https://github.com/mout12/lol.git`
- Main branch: `main`
- S3 bucket: `lol-buck-mx`
- Deployed object: `s3://lol-buck-mx/index.html`
- AWS account used for deploy role: `<account-id>`
- GitHub Actions workflow: `.github/workflows/deploy-s3.yml`
- AWS deploy role: `arn:aws:iam::<account-id>:role/github-lol-s3-deploy`

## Sessions

### 2026-04-25 - Added Admin URL Descriptions

#### What Changed

Added an optional `Description` field to `admin.html` when setting the redirect URL.

Updated `lol-update-current-json` so submitted descriptions are stored in `s3://lol-buck-mx/history.json` alongside the URL and timestamp. `current.json` still stores only the full active URL.

History display behavior:

- If a history item has a description, the admin page displays the full description.
- If a history item has no description, the admin page displays the URL as a single truncated line.
- The current active redirect panel continues to show the full URL.

### 2026-04-25 - Completed Admin URL Visibility And History Work

#### What Changed

Completed the planned admin URL visibility and history slice:

1. `admin.html` now displays the current active redirect URL by reading `./current.json`.
2. `admin.html` now displays prior URL submissions by reading `./history.json`.
3. Tapping a prior URL calls the protected `POST /current` endpoint to make that URL active again.

Updated `lol-update-current-json` so every successful redirect update also maintains `s3://lol-buck-mx/history.json`.

Updated the Lambda execution role so it can:

```text
s3:PutObject -> arn:aws:s3:::lol-buck-mx/current.json
s3:PutObject -> arn:aws:s3:::lol-buck-mx/history.json
s3:GetObject -> arn:aws:s3:::lol-buck-mx/history.json
```

Removed `current.json` from the GitHub Actions deploy workflow. This prevents ordinary code/doc pushes from overwriting the redirect URL selected through the admin page.

#### Verification

Deployed the updated Lambda code and invoked it with the current active redirect URL.

Verified that `s3://lol-buck-mx/history.json` was created with the active URL and no-store cache headers.

Ran lightweight checks against `admin.html` to confirm the current URL display, history rendering, and tap-to-select code paths are present.

#### Remaining Follow-Up

The admin API CORS setting is still open for prototype testing. Restrict it after `admin.lol.buck.mx` is configured.

### 2026-04-25 - Planned Admin URL Visibility And History Work

#### Planned Next Tasks

The next implementation slice is the first three admin quality-of-life items:

1. Show the current active redirect URL on the admin page.
2. Keep and display a list of prior URL submissions.
3. Allow tapping a prior URL from that list to make it the active redirect again.

After these are implemented and verified, add a follow-up session log entry confirming completion and noting any remaining limitations.

### 2026-04-25 - Added Admin Set Redirect Form

#### What Changed

Updated `admin.html` so a signed-in admin can paste a URL and submit it to:

```text
POST https://gil40t7dfi.execute-api.us-east-2.amazonaws.com/current
```

The page sends the Cognito ID token as a bearer token and validates that the URL uses `http://` or `https://` before making the request.

The admin page still does not list prior URL submissions.

### 2026-04-25 - Added Admin Login Page Prototype

#### What Changed

Added `admin.html`, a standalone mobile-friendly Cognito login/logout page.

The page supports:

- normal Cognito username/password login
- first-login `NEW_PASSWORD_REQUIRED` password change
- session display after credentials are accepted
- sign out by clearing browser `sessionStorage`

The page does not call `POST /current` yet and cannot change the redirect target.

Updated the GitHub Actions deploy workflow to upload:

```text
s3://lol-buck-mx/admin.html
```

#### AWS Permission Update

Updated the GitHub Actions deploy role policy to allow `s3:PutObject` on exactly:

```text
arn:aws:s3:::lol-buck-mx/index.html
arn:aws:s3:::lol-buck-mx/current.json
arn:aws:s3:::lol-buck-mx/admin.html
```

### 2026-04-25 - Created Real Cognito Admin User

#### What Changed

Created the real Cognito admin user for the owner email address.

```text
<admin-email>
```

The user is enabled in the `lol-admin-users` user pool and is currently in:

```text
FORCE_CHANGE_PASSWORD
```

This is expected until the first login completes and a permanent password is set. Cognito was allowed to send the invite/temporary password by email rather than recording a password in the repo or chat.

Updated `docs/admin-api.md` with the admin user status.

#### Next Step

Build the minimal admin login page so the admin user can complete the first-login password change and then call the protected `POST /current` endpoint from a phone.

### 2026-04-25 - Admin Redirect Goal Progress Checkpoint

#### Goal

Build toward a phone-friendly admin page where the owner can log in, paste redirect URLs, see previous submissions, and select the active URL that public visitors are redirected to.

#### Current State

The public redirect path is working:

```text
visitor -> lol.buck.mx / cached GoDaddy 301 -> S3 index.html -> S3 current.json -> selected URL
```

`current.json` is currently the source of truth for the active redirect URL.

A protected backend write path now exists:

```text
authenticated POST /current -> API Gateway -> Cognito JWT authorizer -> Lambda -> overwrite s3://lol-buck-mx/current.json
```

The protected endpoint was tested successfully with a disposable Cognito user, and unauthenticated requests returned `401 Unauthorized`.

No real admin user or admin page exists yet.

#### Next Steps

1. Create the real admin Cognito user.
2. Build a minimal mobile-friendly admin page that can log in and call `POST /current`.
3. Deploy the admin page for testing, initially on S3 or a simple path.
4. Add storage for prior URL submissions. The simplest prototype can use an S3 `history.json`; a more durable version can use DynamoDB.
5. Add admin UI list behavior: show prior URLs, add a pasted URL, and tap a prior URL to make it active.
6. Configure `admin.lol.buck.mx` once the basic admin page works.
7. Restrict API CORS from the current prototype `*` origin to the real admin origin after the admin domain is configured.
8. Once the admin flow is reliable, stop treating GitHub edits to `current.json` as the normal management path. GitHub should remain the code/deploy path, while the admin page becomes the URL management path.

### 2026-04-25 - Protected Admin API Prototype

#### What Changed

Created a Cognito-protected HTTP API route for updating the active redirect URL through the existing Lambda writer.

AWS resources:

```text
Cognito user pool: lol-admin-users / us-east-2_J0l6jb3qZ
Cognito app client: lol-admin-web / mjj7ggl6ti48cu6s8qutdek1k
HTTP API: lol-admin-api / gil40t7dfi
HTTP API endpoint: https://gil40t7dfi.execute-api.us-east-2.amazonaws.com
Protected route: POST /current
Authorizer: lol-admin-cognito / 0gnx1a
Lambda integration: lol-update-current-json
```

Added `docs/admin-api.md` with the non-secret resource IDs and current limits.

#### Verification

Called `POST /current` without an authorization token. API Gateway returned `401 Unauthorized`.

Created a disposable Cognito test user, authenticated once, and called `POST /current` with a bearer token. The endpoint returned `200` and wrote the expected URL to `s3://lol-buck-mx/current.json`.

Deleted the disposable Cognito test user and removed local temporary auth files.

#### Follow-Up

No real admin user exists yet. The next step is to create the actual admin login path and a small mobile admin page. CORS is currently open for prototype testing and should be restricted once `admin.lol.buck.mx` is configured.

### 2026-04-25 - Added Lambda Writer Source

#### What Changed

Added repo-tracked Lambda source under `lambda/update_current_json.py` for updating `s3://lol-buck-mx/current.json`.

The Lambda validates that submitted URLs use `http://` or `https://`, then writes `current.json` with no-store cache headers.

#### AWS Resources Created

Created Lambda execution role:

```text
lambda-lol-current-json-writer
```

The role has basic Lambda logging permission and an inline policy allowing `s3:PutObject` only on:

```text
arn:aws:s3:::lol-buck-mx/current.json
```

Created Lambda function:

```text
lol-update-current-json
```

The function uses:

```text
runtime: python3.12
handler: update_current_json.handler
environment:
  REDIRECT_BUCKET=lol-buck-mx
  REDIRECT_KEY=current.json
```

#### Verification

Invoked the Lambda with the current active redirect URL. It returned status 200 and wrote the expected JSON to `s3://lol-buck-mx/current.json`.

Invoked the Lambda with `javascript:alert(1)`. The function returned application-level status 400 and did not accept the URL.

The Lambda has not been exposed through a public API yet.

### 2026-04-25 - Updated Active Redirect Target

#### What Changed

Updated `current.json` so the active redirect target matches the April 25 URL from the prior date-based redirect logic instead of `https://x.com`.

### 2026-04-25 - Repo-Managed Redirect Target Prototype

#### What Changed

Replaced the date-based redirect logic in `index.html` with a fetch of `./current.json`.

Added `current.json` as the repo-managed source of truth for the active redirect URL:

```json
{
  "url": "https://x.com"
}
```

Updated the GitHub Actions S3 deploy workflow to upload both `index.html` and `current.json` with no-store cache headers.

#### AWS Permission Update

The first GitHub Actions deploy after this change failed because the AWS deploy role only allowed `s3:PutObject` on `s3://lol-buck-mx/index.html`.

The inline role policy `AllowUploadLolIndexHtml` was updated to allow `s3:PutObject` on exactly:

```text
arn:aws:s3:::lol-buck-mx/index.html
arn:aws:s3:::lol-buck-mx/current.json
```

The failed deploy run was rerun successfully after the policy update.

### 2026-04-25 - Redacted AWS Identifiers From Public Logs

#### What Changed

After the initial AI session log was added, the user manually squashed the log-file commits and force-pushed the cleaned history to GitHub.

The workflow was then updated to read the deploy role ARN from a GitHub Actions secret instead of a GitHub Actions variable:

```yaml
role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
```

This prevents future GitHub Actions logs from printing the full AWS role ARN.

The old unmasked GitHub Actions variable was deleted after the secret was created.

#### Verification

- Current branch content is redacted.
- GitHub code search did not find the AWS account number.
- GitHub commit search did not find the AWS account number.
- Old workflow runs that printed the unmasked role ARN were deleted.
- The latest workflow run showed the role as `***` in logs.

#### Residual Risk

Some old unreachable commits may remain directly retrievable by full SHA for some period after a force-push. They are no longer reachable from branches or tags, and they did not appear in GitHub search during this session. If full purging is required, use GitHub Support's sensitive-data removal process.

### 2026-04-25 - Initial Local Repo, GitHub Push, and S3 Auto-Deploy

#### What Changed

Downloaded the S3-hosted page into:

```text
~/Projects/lol/index.html
```

Initialized `~/Projects/lol` as a Git repository, connected it to:

```text
https://github.com/mout12/lol.git
```

and pushed it to GitHub.

Set up automatic deployment:

```text
GitHub push to main -> GitHub Actions -> AWS OIDC role -> S3 upload
```

The deploy workflow uploads only:

```text
index.html -> s3://lol-buck-mx/index.html
```

#### Deployment Design

The workflow uses AWS OIDC instead of storing long-lived AWS access keys in GitHub.

When the workflow runs, GitHub requests short-lived AWS credentials. AWS grants those credentials only when the request comes from:

```text
repo:mout12/lol:ref:refs/heads/main
```

The AWS role is:

```text
arn:aws:iam::<account-id>:role/github-lol-s3-deploy
```

Its S3 permission is intentionally narrow. It can only run:

```text
s3:PutObject
```

on:

```text
arn:aws:s3:::lol-buck-mx/index.html
```

That means the GitHub Actions deploy role should only be able to overwrite that one HTML file. It should not be able to list buckets, delete objects, create servers, read secrets, create IAM users, or spend money on EC2.

#### Security And Risk Notes

The biggest risk is GitHub repo control. If someone can push to `mout12/lol` on `main`, they can change the webpage because pushes deploy automatically.

The AWS deploy role itself is tightly scoped, so a compromised GitHub workflow should not create a large AWS bill directly. The role cannot launch infrastructure. The worst expected AWS-side impact from this role is overwriting `index.html`.

There is still a webpage-content risk: someone who can edit `index.html` could redirect visitors to malicious pages. That is not an AWS billing risk, but it is a trust and safety risk for anyone visiting the page.

During this session, local tools were authenticated:

- GitHub CLI logged in as `mout12`.
- AWS CLI logged into the AWS account that owns the `lol-buck-mx` bucket.

Someone with access to this Mac user account may be able to use `gh` or `aws` as the authenticated user, depending on how those credentials are stored and whether they expire.

#### AWS Billing Risk

From the deploy role created in this session, the direct large-bill risk is very low. It only writes one small S3 object.

More realistic AWS bill risks are separate from this deploy role:

- The S3 bucket is public and gets huge traffic.
- Large files in the bucket get downloaded many times.
- CloudFront, if added later, serves massive traffic.
- Some other AWS credential in the account has broad permissions.

For this specific deploy flow, each deploy uploads a roughly 2.8 KB file, which is effectively negligible cost.

#### Follow-Up Hardening

- Enable GitHub 2FA if it is not already enabled.
- Protect the `main` branch in GitHub repo settings.
- Add an AWS budget and billing alarm.
- Consider revoking local sessions when no longer needed:

```bash
gh auth logout
aws logout
```

#### Verification

The GitHub Actions deploy workflow completed successfully after AWS OIDC was configured.

S3 confirmed `index.html` was updated at:

```text
2026-04-25T17:23:43+00:00
```
