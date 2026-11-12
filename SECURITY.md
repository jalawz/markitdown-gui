# Security Policy

## Supported Versions

| Version | Supported |
|---------|:---------:|
| 1.1.x   | ✅ |
| < 1.1   | ❌ |

## Reporting a Vulnerability

Found a security issue? Report it privately via
[GitHub Security Advisories](https://github.com/jalawz/markitdown-gui/security/advisories/new)
instead of opening a public issue.

Please include:
- Description of the vulnerability and its impact
- Steps to reproduce
- Affected version and OS

I'll aim to acknowledge within 48 hours and provide a fix within 7 days.

## Scope

This is a local desktop application that converts documents to Markdown. It has
no network listeners, no telemetry, and no authentication layer by design.

### In scope

- Code execution through malicious documents (e.g., via a MarkItDown dependency)
- Path traversal when writing output files
- Command injection in the file-manager launcher
- Unsafe handling of untrusted input paths

### Out of scope

- Vulnerabilities in [Microsoft MarkItDown](https://github.com/microsoft/markitdown)
  — report those upstream
- Vulnerabilities in Python, tkinter, or the OS
- Denial of service by feeding a legitimately huge file

## Security Considerations for Users

This tool runs with the privileges of your user account. When converting
documents from untrusted sources:

1. Prefer the CLI (`--no-gui`) over the GUI in automated pipelines
2. Be aware that PDFs can contain embedded JavaScript — MarkItDown's
   extraction is read-only, but update your dependencies regularly
3. Don't run the app as administrator
4. Keep `markitdown` updated to pick up fixes in the conversion libraries
