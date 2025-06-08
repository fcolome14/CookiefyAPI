"""Add scoring to tables

Revision ID: e2a438457a07
Revises: 1a91334a041e
Create Date: 2025-06-01 17:57:04.109860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e2a438457a07'
down_revision: Union[str, None] = '1a91334a041e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sites', sa.Column('score', sa.Float(), nullable=True, server_default=sa.text('0.0')))
    op.add_column('sites', sa.Column('click_count', sa.Integer(), nullable=True, server_default=sa.text('0')))
    op.add_column('sites', sa.Column('lists_count', sa.Integer(), nullable=True, server_default=sa.text('0')))
    op.add_column('lists', sa.Column('score', sa.Float(), nullable=True, server_default=sa.text('0.0')))
    op.add_column('lists', sa.Column('visit_count', sa.Integer(), nullable=True, server_default=sa.text('0')))
    op.add_column('hashtags', sa.Column('score', sa.Float(), nullable=True, server_default=sa.text('0.0')))
    op.add_column('hashtags', sa.Column('usage_count', sa.Integer(), nullable=True, server_default=sa.text('0')))


def downgrade() -> None:
    op.drop_column('hashtags', 'usage_count')
    op.drop_column('hashtags', 'score')
    op.drop_column('lists', 'visit_count')
    op.drop_column('lists', 'score')
    op.drop_column('sites', 'lists_count')
    op.drop_column('sites', 'click_count')
    op.drop_column('sites', 'score')