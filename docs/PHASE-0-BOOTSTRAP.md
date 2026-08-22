# Phase 0 bootstrap checklist

This checklist is intentionally limited to the foundation gate. It does not create a product site and it does not publish anything on Manus.

## 1. Add Telegram Actions Secrets

From the repository page on GitHub, open **Settings → Secrets and variables → Actions → New repository secret** and create the following two secrets:

| Secret name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | The token issued by BotFather for the notification bot |
| `TELEGRAM_CHAT_ID` | The destination chat or channel identifier that the bot can message |

The values must be entered directly into GitHub's secret fields. They must not be committed to the repository, pasted into workflow files, or added to the README.

## 2. Run the manual test

Open the repository's **Actions** tab, choose **Phase 0 — Telegram plumbing test**, select **Run workflow**, and confirm the default branch. A successful run means the workflow validated both secrets and Telegram accepted the test message. A failed run must be fixed before Phase 0 is marked complete.

## 3. Enable GitHub Pages

After the repository has at least one commit, open **Settings → Pages**. Under **Build and deployment**, select **Deploy from a branch**, choose the `main` branch and the `/ (root)` folder, then save. This only prepares the repository's GitHub Pages capability; no product page is created in Phase 0.

## 4. Evidence required to close the gate

Phase 0 is complete only when the repository is public, the workflow exists on the `main` branch, the Telegram workflow run is green, and Pages reports that deployment from `main` is configured. Record the workflow run URL and Pages status in the repository README before starting Phase 1.
