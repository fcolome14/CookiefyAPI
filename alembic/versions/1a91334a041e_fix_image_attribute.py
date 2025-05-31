"""Fix image attribute

Revision ID: 1a91334a041e
Revises: 1bff7f9d4fb8
Create Date: 2025-05-31 19:58:04.731381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1a91334a041e'
down_revision: Union[str, None] = '1bff7f9d4fb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename the column `image` to `image_id`
    op.alter_column('sites', 'image', new_column_name='image_id')

    # Drop old index and create a new one for the renamed column
    op.drop_index('ix_sites_image', table_name='sites')
    op.create_index('ix_sites_image_id', 'sites', ['image_id'], unique=False)



def downgrade() -> None:
    # Revert the column name and index
    op.alter_column('sites', 'image_id', new_column_name='image')
    op.drop_index('ix_sites_image_id', table_name='sites')
    op.create_index('ix_sites_image', 'sites', ['image'], unique=False)