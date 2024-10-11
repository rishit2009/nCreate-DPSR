"""empty message

Revision ID: 3105627e5c3b
Revises: 
Create Date: 2024-10-11 03:52:43.787616

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3105627e5c3b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('club', sa.Integer(), nullable=True),
    sa.Column('golds', sa.Integer(), nullable=True),
    sa.Column('silvers', sa.Integer(), nullable=True),
    sa.Column('bronzes', sa.Integer(), nullable=True),
    sa.Column('total', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
