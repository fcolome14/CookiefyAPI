"""create sites table

Revision ID: 579171a476d7
Revises: ad3d4bc7b385
Create Date: 2025-05-14 15:13:48.144107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '579171a476d7'
down_revision: Union[str, None] = 'ad3d4bc7b385'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create referenced tables first
    op.create_table(
        'images',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('data', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'hashtags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create main table after referenced ones
    op.create_table(
        'sites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('image', sa.Integer(), sa.ForeignKey('images.id'), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('contact', sa.String(), nullable=True),
        sa.Column('category', sa.Integer(), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('hashtags', sa.Integer(), sa.ForeignKey('hashtags.id'), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Add indexes
    op.create_index(op.f('ix_sites_id'), 'sites', ['id'], unique=False)
    op.create_index(op.f('ix_sites_address'), 'sites', ['address'], unique=False)
    op.create_index(op.f('ix_sites_image'), 'sites', ['image'], unique=False)
    op.create_index(op.f('ix_sites_category'), 'sites', ['category'], unique=False)
    op.create_index(op.f('ix_sites_hashtags'), 'sites', ['hashtags'], unique=False)


def downgrade() -> None:
    # Drop indexes before dropping the table
    op.drop_index(op.f('ix_sites_hashtags'), table_name='sites')
    op.drop_index(op.f('ix_sites_category'), table_name='sites')
    op.drop_index(op.f('ix_sites_image'), table_name='sites')
    op.drop_index(op.f('ix_sites_address'), table_name='sites')
    op.drop_index(op.f('ix_sites_id'), table_name='sites')
    
    op.drop_table('sites')
    op.drop_table('hashtags')
    op.drop_table('categories')
    op.drop_table('images')