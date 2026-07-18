# Meta API Troubleshooting Guide

This guide explains what to do when `.env` is detected but Meta still returns a permission or read-check error.

## Current known scenario

You may see:

```text
dry_run: true
meta_credentials_present: true
meta_ad_account_id_present: true
meta_page_id_present: true
meta_access_token_present: true
read_check_status: failed
page_check_status: skipped
error_category: permission_error
```

This means the repo can read `.env`, but Meta rejected the ad account read request.

It does **not** mean the local repo is broken.

---

## Important distinction

A new or empty ad account should return:

```json
{
  "data": []
}
```

That is a valid response. It means the account is readable, but there are no campaigns yet.

A permission problem returns something like:

```text
(#200) Ad account owner has NOT grant ads_management or ads_read permission
```

or:

```text
403 Forbidden
```

That means the token cannot read campaign objects from the ad account yet.

---

## Confirm the token can see ad accounts

Run this from the project folder:

```powershell
cd "C:\Users\vanne\OneDrive\Documents\Personal Projects\Meta-Ads-Campaign"

$token = (Get-Content .env | Where-Object { $_ -match '^META_ACCESS_TOKEN=' }) -replace '^META_ACCESS_TOKEN=', ''
$token = $token.Trim().Trim('"').Trim("'")
$encodedToken = [uri]::EscapeDataString($token)

Invoke-RestMethod -Uri "https://graph.facebook.com/v20.0/me/adaccounts?fields=id,name,account_status&access_token=$encodedToken" | ConvertTo-Json -Depth 6
```

Expected account:

```text
act_1073750411852591 = Glow Grow Studio
```

If the account appears here, the token has visibility to the ad account list.

---

## Test the exact campaign endpoint

Run:

```powershell
Invoke-RestMethod -Uri "https://graph.facebook.com/v20.0/act_1073750411852591/campaigns?fields=id,name,status,effective_status&limit=10&access_token=$encodedToken" | ConvertTo-Json -Depth 6
```

### Good result

```json
{
  "data": []
}
```

This is okay for a new ad account.

### Bad result

```text
403 Forbidden
```

or:

```text
(#200) Ad account owner has NOT grant ads_management or ads_read permission
```

This means the issue is still inside Meta permissions or business asset assignment.

---

## Confirm token permissions

Run:

```powershell
Invoke-RestMethod -Uri "https://graph.facebook.com/v20.0/me/permissions?access_token=$encodedToken" | ConvertTo-Json -Depth 6
```

Look for:

```text
ads_read: granted
ads_management: granted
business_management: granted
pages_show_list: granted
pages_manage_ads: granted
```

If `ads_read` and `ads_management` are granted but the campaign endpoint still fails, the problem is usually **asset assignment**, not the permission name itself.

---

## Meta asset assignment checklist

In Meta Business Settings, check all three areas.

### 1. System user asset access

```text
Business Settings
→ Users
→ System users
→ Select system user
→ Assigned assets
```

The system user should have access to:

```text
Facebook Page: Glow & Grow Circle / Founders Club related page
Ad Account: Glow Grow Studio
App: Secrecy
```

The missing one is often the **Ad Account**.

### 2. App asset access

```text
Business Settings
→ Accounts
→ Apps
→ Secrecy
```

Confirm the app is connected to:

```text
Ad Account: Glow Grow Studio
Page: Glow & Grow Circle / Founders Club related page
```

### 3. Ad account people/system user access

```text
Business Settings
→ Accounts
→ Ad accounts
→ Glow Grow Studio
→ People / System users
```

Confirm the system user or your own user has full access.

After changing any asset access, generate a **new system user token**.

---

## Do not block local creative work

If `meta_auth_check.py` still fails but the account is new and you are not ready to pull Meta reports yet, continue with the safe local workflow:

```bash
python src/meta_ads_mvp.py
```

Then review:

```text
outputs/facebook_ad_drafts.csv
outputs/instagram_caption_drafts.csv
outputs/content_calendar.csv
outputs/compliance_review.csv
```

This workflow does not touch Meta Ads Manager.

---

## Safe next workflow while Meta read is pending

Use this order:

```text
1. Generate local campaign drafts.
2. Review compliance output.
3. Manually edit approved draft rows.
4. Keep DRY_RUN=true.
5. Run dry-run uploader only after approval fields are complete.
6. Do not create active campaigns.
7. Do not publish automatically.
```

---

## What not to do

Do not commit:

```text
.env
.env.txt
access tokens
app secrets
customer lists
real private ad exports
```

Do not bypass:

```text
approval_guard.py
DRY_RUN=true
REQUIRE_HUMAN_APPROVAL=true
```

Do not change any live campaign until the read-only and dry-run flow is stable.
