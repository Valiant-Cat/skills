# Feishu IM Upload (image/file)

> Source: Feishu Open Platform docs (IM v1) — Upload image / Upload file.
> If any field names or enums look off, re-check the official docs before calling.

## Auth
- **Authorization**: `Bearer <tenant_access_token | app_access_token>`
- **Content-Type**: `multipart/form-data`

## Upload Image
- **Endpoint**: `POST https://open.feishu.cn/open-apis/im/v1/images`
- **Form fields**:
  - `image_type` (string): image type enum. Common values:
    - `message` (message image)
    - `avatar` (user/group avatar)
    - `chat` (group avatar)
    - `open_graph` (link preview)
  - `image` (file): binary image file

**Response**: `image_key` (string)

**curl**
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "image_type=message" \
  -F "image=@/path/to/image.png" \
  https://open.feishu.cn/open-apis/im/v1/images
```

## Upload File
- **Endpoint**: `POST https://open.feishu.cn/open-apis/im/v1/files`
- **Form fields**:
  - `file_type` (string): file type enum. Common values:
    - `stream` (general file)
    - `image` (image file)
    - `doc` / `xls` / `ppt` / `pdf` (document types)
  - `file` (file): binary file

**Response**: `file_key` (string)

**curl**
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=stream" \
  -F "file=@/path/to/file.zip" \
  https://open.feishu.cn/open-apis/im/v1/files
```

## Notes
- Ensure files respect size/type constraints in the official docs.
- Returned `image_key` / `file_key` are used when sending messages via IM APIs.
- **Video cover**: for `msg_type=media`, set `image_key` to the **first frame** of the video.

### Extract first frame (cover)
```bash
ffmpeg -y -i /path/to/video.mp4 -frames:v 1 /path/to/cover.jpg
```
Upload `cover.jpg` via Upload Image (`image_type=message`) and use the returned `image_key` in the media message content.
