"""empty message

Revision ID: 890f4e443442
Revises: b823ee201761
Create Date: 2020-03-02 17:12:48.074217

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '890f4e443442'
down_revision = 'b823ee201761'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ActionPlan',
    sa.Column('actionPlanId', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.Column('stepName', sa.String(length=255), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['userId'], ['User.idNum'], ),
    sa.PrimaryKeyConstraint('actionPlanId'),
    sa.UniqueConstraint('actionPlanId')
    )
    op.create_table('Entry',
    sa.Column('entryid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('action_plan_one', sa.String(length=255), nullable=False),
    sa.Column('action_plan_two', sa.String(length=255), nullable=True),
    sa.Column('action_plan_three', sa.String(length=255), nullable=True),
    sa.Column('action_plan_four', sa.String(length=255), nullable=True),
    sa.Column('action_plan_five', sa.String(length=255), nullable=True),
    sa.Column('goal_rating', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.idNum'], ),
    sa.PrimaryKeyConstraint('entryid'),
    sa.UniqueConstraint('entryid')
    )
    op.drop_table('entry')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('entry',
    sa.Column('entryid', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('action_plan_one', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('action_plan_two', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('action_plan_three', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('action_plan_four', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('action_plan_five', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('date', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('goal_rating', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.idNum'], name='entry_user_id_fkey'),
    sa.PrimaryKeyConstraint('entryid', name='entry_pkey'),
    sa.UniqueConstraint('entryid', name='entry_entryid_key')
    )
    op.drop_table('Entry')
    op.drop_table('ActionPlan')
    # ### end Alembic commands ###