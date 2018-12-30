"""Refactor AWS

Revision ID: 9888ff06109d
Revises: b0d466dc284e
Create Date: 2018-12-30 19:37:34.369958

"""

from alembic import op

import sqlalchemy as sa

from yui.orm.type import TimezoneType

# revision identifiers, used by Alembic.
revision = '9888ff06109d'
down_revision = 'b0d466dc284e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('aws')


def downgrade():
    op.create_table(
        'aws',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('is_raining', sa.Boolean(), nullable=True),
        sa.Column('rain15', sa.Float(), nullable=True),
        sa.Column('rain60', sa.Float(), nullable=True),
        sa.Column('rain3h', sa.Float(), nullable=True),
        sa.Column('rain6h', sa.Float(), nullable=True),
        sa.Column('rain12h', sa.Float(), nullable=True),
        sa.Column('rainday', sa.Float(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('wind_direction1', sa.String(), nullable=True),
        sa.Column('wind_speed1', sa.Float(), nullable=True),
        sa.Column('wind_direction10', sa.String(), nullable=True),
        sa.Column('wind_speed10', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Integer(), nullable=True),
        sa.Column('pressure', sa.Float(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('observed_datetime', sa.DateTime(), nullable=False),
        sa.Column('observed_timezone', TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
