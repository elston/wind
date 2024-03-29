"""Add WU daily limit

Revision ID: 6440a41d0a8e
Revises: 7e95c1f23234
Create Date: 2016-07-20 15:59:06.907526

"""

# revision identifiers, used by Alembic.
revision = '6440a41d0a8e'
down_revision = '7e95c1f23234'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wu_daily_count',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wu_daily_count')
    ### end Alembic commands ###
