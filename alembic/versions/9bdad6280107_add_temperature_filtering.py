"""Add temperature filtering

Revision ID: 9bdad6280107
Revises: 6c32da3e0490
Create Date: 2016-09-01 10:44:22.747871

"""

# revision identifiers, used by Alembic.
revision = '9bdad6280107'
down_revision = '6c32da3e0490'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('observations', sa.Column('tempm_raw', sa.Float(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('observations', 'tempm_raw')
    ### end Alembic commands ###
