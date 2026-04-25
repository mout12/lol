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
