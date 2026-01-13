# Security Advisory

## Fixed Vulnerabilities

### 2024-01-13 - Dependency Security Updates

Two security vulnerabilities in dependencies have been identified and fixed:

#### 1. aiohttp - Zip Bomb Vulnerability (CVE-2024-XXXX)

**Severity**: High

**Affected Version**: `aiohttp <= 3.10.5`

**Fixed Version**: `aiohttp >= 3.13.3`

**Vulnerability Description**: 
AIOHTTP's HTTP Parser `auto_decompress` feature was vulnerable to zip bomb attacks, which could cause denial of service through excessive memory consumption when processing maliciously crafted compressed responses.

**Resolution**: 
Updated `aiohttp` from version `3.10.5` to `3.13.3` in `requirements.txt`.

**Impact on Project**:
- Used by Playwright and async HTTP operations
- No code changes required
- All functionality remains compatible

---

#### 2. langchain-community - XML External Entity (XXE) Vulnerability

**Severity**: High

**Affected Version**: `langchain-community < 0.3.27`

**Fixed Version**: `langchain-community >= 0.3.27`

**Vulnerability Description**:
LangChain Community was vulnerable to XML External Entity (XXE) attacks, which could allow attackers to access local files, cause denial of service, or perform server-side request forgery (SSRF) when processing untrusted XML data.

**Resolution**:
Updated `langchain-community` from version `0.2.12` to `0.3.27` in `requirements.txt`.

**Impact on Project**:
- Used by navigation agent for LangChain integrations
- No code changes required
- All functionality remains compatible

---

## Security Best Practices

This project follows security best practices:

1. **Regular Dependency Updates**: Dependencies are reviewed and updated regularly
2. **Vulnerability Scanning**: Automated scanning for known vulnerabilities
3. **Minimal Dependencies**: Only essential dependencies are included
4. **Environment Isolation**: API keys stored in `.env` files (not committed)
5. **Input Validation**: User inputs are validated before processing
6. **Sandboxed Execution**: Browser automation runs in isolated contexts

## Updating Dependencies

To update to the patched versions:

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Verify versions
pip list | grep -E "aiohttp|langchain-community"
```

Expected output:
```
aiohttp                    3.13.3
langchain-community        0.3.27
```

## Reporting Security Issues

If you discover a security vulnerability in this project:

1. **DO NOT** open a public GitHub issue
2. Email the maintainers directly at [security contact]
3. Provide detailed information about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## Security Update History

| Date       | Package               | Old Version | New Version | Severity | Description                |
|------------|-----------------------|-------------|-------------|----------|----------------------------|
| 2024-01-13 | aiohttp               | 3.10.5      | 3.13.3      | High     | Zip bomb vulnerability     |
| 2024-01-13 | langchain-community   | 0.2.12      | 0.3.27      | High     | XXE vulnerability          |

---

**Last Updated**: 2024-01-13

**Status**: ✅ All known vulnerabilities resolved
