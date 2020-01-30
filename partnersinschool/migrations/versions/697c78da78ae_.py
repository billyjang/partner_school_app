"""empty message

Revision ID: 697c78da78ae
Revises: 491f513b885e
Create Date: 2020-01-30 00:19:52.736657

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '697c78da78ae'
down_revision = '491f513b885e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('userid', sa.Integer(), autoincrement=True, nullable=False))
    op.drop_column('User', 'uid')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('uid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('User', 'userid')
    # ### end Alembic commands ###
