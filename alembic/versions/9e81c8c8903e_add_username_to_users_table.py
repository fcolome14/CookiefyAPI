"""Add username to Users  table

Revision ID: 9e81c8c8903e
Revises: ad3d4bc7b385
Create Date: 2025-02-23 16:54:58.948830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e81c8c8903e'
down_revision: Union[str, None] = 'ad3d4bc7b385'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.create_index('ix_users_username', 'users', ['username'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_username', table_name='users')
    op.drop_column('users', 'username')
