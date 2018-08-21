"""Drop SiteSub(watch)

Revision ID: c77609c62c8c
Revises: 5e8ae030c78d
Create Date: 2018-08-21 16:23:40.451284

"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c77609c62c8c'
down_revision = '5e8ae030c78d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('site_sub')


def downgrade():
    op.create_table(
        'site_sub',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('url', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('user', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('body', sa.TEXT(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='site_sub_pkey'),
    )
