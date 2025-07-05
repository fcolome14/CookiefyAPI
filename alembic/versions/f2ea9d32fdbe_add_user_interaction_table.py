"""Add user interaction table

Revision ID: f2ea9d32fdbe
Revises: d1874870e00f
Create Date: 2025-07-05 13:04:18.738534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f2ea9d32fdbe'
down_revision: Union[str, None] = 'd1874870e00f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_interactions',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.Integer, nullable=False),
        sa.Column('interaction_type', sa.String(50), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    )

    op.create_index(
        'idx_user_entity_interaction',
        'user_interactions',
        ['user_id', 'entity_type', 'entity_id', 'interaction_type']
    )

    op.create_index(
        'idx_entity_interaction_type',
        'user_interactions',
        ['entity_type', 'entity_id', 'interaction_type']
    )

    # Correct partial unique index for "like" interactions
    op.execute("""
        CREATE UNIQUE INDEX uq_user_entity_like
        ON user_interactions (user_id, entity_type, entity_id)
        WHERE interaction_type = 'like';
    """)


def downgrade() -> None:
    op.execute("DROP INDEX uq_user_entity_like")
    op.drop_index('idx_entity_interaction_type', table_name='user_interactions')
    op.drop_index('idx_user_entity_interaction', table_name='user_interactions')
    op.drop_table('user_interactions')