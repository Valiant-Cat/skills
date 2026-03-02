---
name: feishu-im
description: Feishu IM API operations. Use when working with Feishu/飞书 IM v1 endpoints, especially uploading images or files (getting image_key/file_key) to send messages or attach media via server APIs.
---

# Feishu IM

## Overview
Use this skill to upload images/files to Feishu IM v1 and obtain `image_key` / `file_key` for message sending. Reference the official docs before execution.

## Quick workflow
1. Confirm which upload type is needed (image vs file) and purpose (message, avatar, document, etc.).
2. **Obtain `tenant_access_token` using appId/appSecret** (if not already available).
   - In this environment, appId/appSecret are stored in `~/.openclaw/openclaw.json` under `channels.feishu.accounts.<account>`.
3. Read **references/im-upload.md** for endpoints, form fields, and example requests.
4. Perform the upload using multipart/form-data with a valid Feishu access token.
5. Use the returned `image_key` / `file_key` in subsequent IM message APIs.

## Tasks

### Upload image
- Load **references/im-upload.md** and follow the Upload Image section.
- Ensure the `image_type` enum matches the target scenario.
- Validate file size/type limits in the official docs.

### Upload file
- Load **references/im-upload.md** and follow the Upload File section.
- Choose correct `file_type` enum (stream vs document types).
- Validate file size/type limits in the official docs.

### Send video with cover
- For `msg_type=media`, include **both** `file_key` and `image_key` in `content`.
- The **cover must be the first frame of the video** (extract first frame → upload as image → use its `image_key`).
- See **references/im-upload.md** for extraction + upload notes.

## References
- **references/im-upload.md** — endpoints, required fields, and curl examples for image/file uploads.
