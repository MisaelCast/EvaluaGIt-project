"""add unassigned user role

Revision ID: 739dca998ec8
Revises: 836f56f8a1c4
Create Date: 2026-05-17 21:29:38.019123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '739dca998ec8'
down_revision: Union[str, Sequence[str], None] = '836f56f8a1c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'UNASSIGNED'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
