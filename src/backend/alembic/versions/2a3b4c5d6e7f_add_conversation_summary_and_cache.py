"""add conversation summary and cache fields

Revision ID: 2a3b4c5d6e7f
Revises: 1dcbcb9a5b2e
Create Date: 2026-09-04 14:41:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a3b4c5d6e7f'
down_revision: Union[str, None] = '1dcbcb9a5b2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('conversations', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('conversations', sa.Column('gemini_cache_name', sa.String(), nullable=True))
    op.add_column('conversations', sa.Column('gemini_cache_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('conversations', 'gemini_cache_expires_at')
    op.drop_column('conversations', 'gemini_cache_name')
    op.drop_column('conversations', 'summary')
