---
name: python-security-supply-chain
description: Trigger when Python dependencies, packaging, publishing, CI hardening, or security scanning are involved. Not for general feature work.
---

# Check
- Ruff security rules enabled
- dependency lock or hash pinning present
- vulnerability audit step present
- SBOM generation present for releases
- Trusted publishing / short-lived credentials preferred
- avoid fresh dependency adoption without cooling-off policy

# Output
- current gaps
- minimal fixes
- release/publishing risks
