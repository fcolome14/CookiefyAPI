"""create lists, update sites and added association tables

Revision ID: 1bff7f9d4fb8
Revises: 579171a476d7
Create Date: 2025-05-16 16:43:31.461336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1bff7f9d4fb8'
down_revision: Union[str, None] = '579171a476d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create `lists` table
    op.create_table(
        'lists',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('owner', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('shares', sa.Integer(), nullable=True),
        sa.Column('saves', sa.Integer(), nullable=True),
        sa.Column('image', sa.Integer(), sa.ForeignKey('images.id')),
        sa.Column('is_banned', sa.Boolean(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('accepts_contributions', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=True),
    )

    # Create `list_site_association` table
    op.create_table(
        'list_site_association',
        sa.Column('list_id', sa.Integer(), sa.ForeignKey('lists.id'), primary_key=True),
        sa.Column('site_id', sa.Integer(), sa.ForeignKey('sites.id'), primary_key=True)
    )

    # Create `site_hashtag_association` table
    op.create_table(
        'site_hashtag_association',
        sa.Column('sites_id', sa.Integer(), sa.ForeignKey('sites.id'), primary_key=True),
        sa.Column('hashtag_id', sa.Integer(), sa.ForeignKey('hashtags.id'), primary_key=True)
    )

    # Optionally drop `sites.hashtags` column if it still exists
    op.drop_column('sites', 'hashtags')  # only if it was a direct FK before



def downgrade():
    op.add_column('sites', sa.Column('hashtags', sa.Integer(), nullable=True))
    op.drop_table('site_hashtag_association')
    op.drop_table('list_site_association')
    op.drop_table('lists')
