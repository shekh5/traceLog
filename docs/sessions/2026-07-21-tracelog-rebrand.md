# Session: TraceLog rebrand

## Scope

Renamed the product and implementation completely to TraceLog. This is a clean break rather
than a display-name-only alias, so source imports and public commands match the product.

## Changes

- Renamed the Python package to `tracelog` and updated every import.
- Renamed the distribution and console commands to `tracelog`, `tracelog-mcp`, and
  `tracelog-gate`.
- Updated product copy, dashboards, metadata, tests, examples, docs, deployment files,
  Phoenix artifact prefixes, meta-project defaults, state collection defaults, and the
  system-override header (`X-TraceLog-Token`).
- Changed Cloud Build's default Artifact Registry repository to `tracelog`.
- Removed hardcoded VM project/image/Phoenix identifiers; the startup script now requires
  `GCP_PROJECT_ID` and `PHOENIX_BASE_URL` and accepts configurable region/repository/tag.

## Compatibility notes

- Existing integrations must change imports from the previous package name to `tracelog`.
- MCP/CI callers must use `tracelog-mcp` and `tracelog-gate`.
- Patient adapters must send `X-TraceLog-Token`.
- Existing Firestore/Phoenix state is not automatically migrated to the new
  `tracelog_state` and `tracelog-meta` defaults.
- The external GitHub repository and cloud resources must be renamed or reconfigured by
  their owners; changing source references does not rename remote resources.

Settings remain process-cached, so restart services after updating environment values.
