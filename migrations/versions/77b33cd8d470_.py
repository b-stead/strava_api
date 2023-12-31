"""empty message

Revision ID: 77b33cd8d470
Revises: bd003fcbbf34
Create Date: 2023-10-14 14:25:55.752810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77b33cd8d470'
down_revision = 'bd003fcbbf34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('club_membership', schema=None) as batch_op:
        batch_op.add_column(sa.Column('joined_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('club_membership', schema=None) as batch_op:
        batch_op.drop_column('joined_at')

    # ### end Alembic commands ###
