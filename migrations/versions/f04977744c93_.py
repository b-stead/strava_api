"""empty message

Revision ID: f04977744c93
Revises: 77b33cd8d470
Create Date: 2023-10-15 16:18:00.379497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f04977744c93'
down_revision = '77b33cd8d470'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('strava_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=True),
    sa.Column('token', sa.String(length=40), nullable=True),
    sa.Column('refresh_token', sa.String(length=40), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('strava_user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_strava_user_timestamp'), ['timestamp'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('strava_user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_strava_user_timestamp'))

    op.drop_table('strava_user')
    # ### end Alembic commands ###