"""Add ARIMA price models to markets table

Revision ID: 72a06f26bf27
Revises: ea2ff712150d
Create Date: 2016-07-29 19:39:02.898976

"""

# revision identifiers, used by Alembic.
import webapp

revision = '72a06f26bf27'
down_revision = 'ea2ff712150d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('markets', sa.Column('MAvsMD_model', webapp.models.arima_price_model.ArimaPriceModel(), nullable=True))
    op.add_column('markets', sa.Column('lambdaD_model', webapp.models.arima_price_model.ArimaPriceModel(), nullable=True))
    op.add_column('markets', sa.Column('sqrt_r_model', webapp.models.arima_price_model.ArimaPriceModel(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('markets', 'sqrt_r_model')
    op.drop_column('markets', 'lambdaD_model')
    op.drop_column('markets', 'MAvsMD_model')
    ### end Alembic commands ###
