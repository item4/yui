"""SAOMD Sim

Revision ID: a48384d2e66c
Revises: 9b794095d9c8
Create Date: 2017-11-03 19:57:41.849043

"""
import enum

from alembic import op

import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'a48384d2e66c'
down_revision = '9b794095d9c8'
branch_labels = None
depends_on = None


class ScoutType(enum.Enum):
    """Scout Type."""

    character = 1
    weapon = 2


class CostType(enum.Enum):
    """Cost Type."""

    diamond = 1
    record_crystal = 2


def upgrade():
    op.create_table(
        'saomd_player',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user', sa.String(length=10), nullable=True),
        sa.Column('characters', sqlalchemy_utils.types.json.JSONType(),
                  nullable=False),
        sa.Column('weapons', sqlalchemy_utils.types.json.JSONType(),
                  nullable=False),
        sa.Column('record_crystals', sqlalchemy_utils.types.json.JSONType(),
                  nullable=False),
        sa.Column('used_diamond', sa.Integer(), nullable=False),
        sa.Column('release_crystal', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user')
    )
    op.create_table(
        'saomd_scout',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column(
            'type',
            sqlalchemy_utils.types.choice.ChoiceType(
                ScoutType,
                impl=sa.Integer(),
            ),
            nullable=False
        ),
        sa.Column('s4_units', sqlalchemy_utils.types.json.JSONType(),
                  nullable=False),
        sa.Column('s5_units', sqlalchemy_utils.types.json.JSONType(),
                  nullable=False),
        sa.Column('record_crystal', sqlalchemy_utils.types.json.JSONType(),
                  nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'saomd_step',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=10), nullable=False),
        sa.Column('scout_id', sa.Integer(), nullable=False),
        sa.Column('is_first', sa.Boolean(), nullable=False),
        sa.Column('cost', sa.Integer(), nullable=False),
        sa.Column(
            'cost_type',
            sqlalchemy_utils.types.choice.ChoiceType(
                CostType,
                impl=sa.Integer(),
            ),
            nullable=False
        ),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('s4_fixed', sa.Integer(), nullable=False),
        sa.Column('s5_fixed', sa.Integer(), nullable=False),
        sa.Column('s4_chance', sa.Float(), nullable=False),
        sa.Column('s5_chance', sa.Float(), nullable=False),
        sa.Column('next_step_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['next_step_id'], ['saomd_step.id'], ),
        sa.ForeignKeyConstraint(['scout_id'], ['saomd_scout.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'saomd_player_scout',
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('scout_id', sa.Integer(), nullable=False),
        sa.Column('next_step_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['next_step_id'], ['saomd_step.id'], ),
        sa.ForeignKeyConstraint(['player_id'], ['saomd_player.id'], ),
        sa.ForeignKeyConstraint(['scout_id'], ['saomd_scout.id'], ),
        sa.PrimaryKeyConstraint('player_id', 'scout_id')
    )


def downgrade():
    op.drop_table('saomd_player_scout')
    op.drop_table('saomd_step')
    op.drop_table('saomd_scout')
    op.drop_table('saomd_player')
