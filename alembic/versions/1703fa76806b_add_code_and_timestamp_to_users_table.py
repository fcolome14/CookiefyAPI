"""Add code and timestamp to Users table

Revision ID: 1703fa76806b
Revises: 9e81c8c8903e
Create Date: 2025-02-23 19:27:11.328602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1703fa76806b'
down_revision: Union[str, None] = '9e81c8c8903e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('code', sa.Integer(), nullable=True))
    op.create_index('ix_users_code', 'users', ['code'], unique=True)
    
    op.add_column(
        'users',
        sa.Column(
            'created_at',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        )
    )

def downgrade() -> None:
    op.drop_index('ix_users_code', table_name='users')

    op.drop_column('users', 'code')
    op.drop_column('users', 'created_at')
