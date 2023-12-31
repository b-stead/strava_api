"""empty message

Revision ID: 2d4448070600
Revises: f04977744c93
Create Date: 2023-10-15 16:24:54.054681

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d4448070600'
down_revision = 'f04977744c93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('strava_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('strava_id', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('strava_user', schema=None) as batch_op:
        batch_op.drop_column('strava_id')

    # ### end Alembic commands ###
