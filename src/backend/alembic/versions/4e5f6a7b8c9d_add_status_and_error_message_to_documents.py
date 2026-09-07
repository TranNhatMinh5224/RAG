"""add status and error_message to documents

Revision ID: 4e5f6a7b8c9d
Revises: 3c4d5e6f7a8b
Create Date: 2026-09-07 10:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e5f6a7b8c9d'
down_revision: Union[str, None] = '3c4d5e6f7a8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('documents', sa.Column('status', sa.String(), nullable=True, server_default='PROCESSING'))
    op.add_column('documents', sa.Column('error_message', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('documents', 'error_message')
    op.drop_column('documents', 'status')
