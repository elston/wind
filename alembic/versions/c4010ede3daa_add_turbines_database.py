"""Add turbines database

Revision ID: c4010ede3daa
Revises: 64a64239efb9
Create Date: 2016-08-06 19:48:24.508774

"""

# revision identifiers, used by Alembic.
revision = 'c4010ede3daa'
down_revision = '64a64239efb9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('turbines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('vertical_axis', sa.Boolean(), nullable=True),
    sa.Column('rotor_diameter', sa.Float(), nullable=True),
    sa.Column('rated_power', sa.Float(), nullable=True),
    sa.Column('v_cutin', sa.Float(), nullable=True),
    sa.Column('v_cutoff', sa.Float(), nullable=True),
    sa.Column('description', sa.Unicode(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('turbine_power_curves',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('turbine_id', sa.Integer(), nullable=True),
    sa.Column('wind_speed', sa.Float(), nullable=True),
    sa.Column('power', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['turbine_id'], ['turbines.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_turbine_power_curves_turbine_id'), 'turbine_power_curves', ['turbine_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_turbine_power_curves_turbine_id'), table_name='turbine_power_curves')
    op.drop_table('turbine_power_curves')
    op.drop_table('turbines')
    ### end Alembic commands ###
