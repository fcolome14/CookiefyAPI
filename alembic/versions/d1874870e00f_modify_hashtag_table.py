"""Modify hashtag table

Revision ID: d1874870e00f
Revises: e2a438457a07
Create Date: 2025-06-15 12:33:01.855862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd1874870e00f'
down_revision: Union[str, None] = 'e2a438457a07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('hashtags', sa.Column('image_id', sa.Integer(), nullable=True, server_default='2'))
    op.create_foreign_key(
        'fk_hashtags_image_id',           # Constraint name
        'hashtags',                       # Source table
        'images',                         # Referenced table
        ['image_id'],                     # Local column
        ['id'],                           # Remote column
        ondelete='SET NULL'               # Optional: set NULL if image is deleted
    )

def downgrade() -> None:
    # Drop FK and column
    op.drop_constraint('fk_hashtags_image_id', 'hashtags', type_='foreignkey')
    op.drop_column('hashtags', 'image_id')