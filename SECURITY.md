# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Report security issues by email to **niwciu@gmail.com** with the subject line:

```
[encrypt-bin] Security Vulnerability Report
```

Include:
- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- The version of encrypt-bin affected

You will receive an acknowledgement within 48 hours. We aim to release a fix within 14 days for confirmed vulnerabilities.

## Security Notes

- AES-128-CBC encryption is used for firmware payload protection. A fresh random IV is generated per output file.
- The CRC32 checksum covers the **padded plaintext** — it is an integrity check, not a cryptographic MAC.
- Key files should be restricted to the owner only (`chmod 600`). encrypt-bin will warn if group/other read permissions are set.
- Keys are handled as plain `bytes` in memory. No memory locking (`mlock`) or secure erasure is performed after use.
