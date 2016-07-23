"""Add db indexes

Revision ID: 83ea6dbbcafe
Revises: 636486d83d03
Create Date: 2016-07-23 13:32:11.543000

"""

# revision identifiers, used by Alembic.
revision = '83ea6dbbcafe'
down_revision = '636486d83d03'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_history_download_status_date'), 'history_download_status', ['date'], unique=False)
    op.create_index(op.f('ix_history_download_status_location_id'), 'history_download_status', ['location_id'], unique=False)
    op.create_index(op.f('ix_locations_user_id'), 'locations', ['user_id'], unique=False)
    op.create_index(op.f('ix_observations_location_id'), 'observations', ['location_id'], unique=False)
    op.create_index(op.f('ix_observations_time'), 'observations', ['time'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_observations_time'), table_name='observations')
    op.drop_index(op.f('ix_observations_location_id'), table_name='observations')
    op.drop_index(op.f('ix_locations_user_id'), table_name='locations')
    op.drop_index(op.f('ix_history_download_status_location_id'), table_name='history_download_status')
    op.drop_index(op.f('ix_history_download_status_date'), table_name='history_download_status')
    ### end Alembic commands ###
