"""RSS Feed

Revision ID: 9b794095d9c8
Revises: 722ab69c73d1
Create Date: 2017-10-18 02:22:12.421786

"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b794095d9c8'
down_revision = '722ab69c73d1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'feed',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('channel', sa.String(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('feed')
