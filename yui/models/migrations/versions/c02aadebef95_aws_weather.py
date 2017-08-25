"""AWS Weather

Revision ID: c02aadebef95
Revises:
Create Date: 2017-08-24 23:11:28.070371

"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c02aadebef95'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'aws',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=15), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('is_raining', sa.Boolean(), nullable=True),
        sa.Column('rain15', sa.Float(), nullable=True),
        sa.Column('rain60', sa.Float(), nullable=True),
        sa.Column('rain6h', sa.Float(), nullable=True),
        sa.Column('rain12h', sa.Float(), nullable=True),
        sa.Column('rainday', sa.Float(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('wind_direction1', sa.String(length=3), nullable=True),
        sa.Column('wind_speed1', sa.Float(), nullable=True),
        sa.Column('wind_direction10', sa.String(length=3), nullable=True),
        sa.Column('wind_speed10', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Integer(), nullable=True),
        sa.Column('pressure', sa.Float(), nullable=True),
        sa.Column('location', sa.String(length=50), nullable=True),
        sa.Column('observed_datetime', sa.DateTime(timezone=True),
                  nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('aws')
