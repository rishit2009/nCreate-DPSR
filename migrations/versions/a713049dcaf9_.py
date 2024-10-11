"""empty message

Revision ID: a713049dcaf9
Revises: 0e8a71b65c3b
Create Date: 2024-10-11 13:20:06.637695

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a713049dcaf9'
down_revision = '0e8a71b65c3b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notifications', sa.PickleType(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('notifications')

    # ### end Alembic commands ###
