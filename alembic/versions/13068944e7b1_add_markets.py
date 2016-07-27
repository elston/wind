"""Add markets

Revision ID: 13068944e7b1
Revises: 83ea6dbbcafe
Create Date: 2016-07-27 18:00:33.356005

"""

# revision identifiers, used by Alembic.
revision = '13068944e7b1'
down_revision = '83ea6dbbcafe'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('markets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_markets_user_id'), 'markets', ['user_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_markets_user_id'), table_name='markets')
    op.drop_table('markets')
    ### end Alembic commands ###
