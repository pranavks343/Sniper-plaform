#!/usr/bin/env python3
"""Generate a strong random secret for CIRCUIT_BREAKER_ADMIN_SECRET. Run once and paste into .env."""
import secrets
print(secrets.token_urlsafe(32))
