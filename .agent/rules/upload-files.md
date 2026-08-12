# Upload and File Rules

Upload handling must be defensive.

Required:

- Sanitize filenames with `Path(file.filename).name`.
- Store files using generated names.
- Never trust user-provided filenames for storage paths.
- Enforce max upload size.
- Validate extension.
- Validate MIME type and magic bytes before production release.
- Store uploads outside source code directories.
- Clean up file and DB record if ingestion fails.
- Avoid blocking request threads with long OCR or ingestion work in production.

Do not log:

- File contents.
- Extracted text.
- Full chunks.
- Sensitive filenames if they may contain private data.

Production target:

```text
upload request -> create document row as queued -> save file/object -> background worker ingests -> document status ready/failed
```

Deletion must handle:

- DB row.
- Stored file/object.
- Vector store points.
- Conversation-document links.
- Partial failure recovery.
