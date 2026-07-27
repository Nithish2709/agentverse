#!/usr/bin/env bash
# Seed a default super-admin user for local development
set -euo pipefail

python - <<'EOF'
import asyncio
from app.config import get_settings
from app.database.session import AsyncSessionLocal
from app.services.user import UserService
from app.schemas.user import UserCreate
from app.core.security import Role
from app.core.exceptions import ConflictError

async def seed():
    async with AsyncSessionLocal() as session:
        svc = UserService(session)
        try:
            user = await svc.create_user(UserCreate(
                email="admin@pds-sentinel.local",
                username="superadmin",
                password="Admin1234",
                full_name="Super Admin",
                role=Role.SUPER_ADMIN,
            ))
            await session.commit()
            print(f"✓ Created super-admin: {user.email}")
        except ConflictError:
            print("⚠ Super-admin already exists — skipping")

asyncio.run(seed())
EOF
