"""empty message

Revision ID: d90bf7b5d206
Revises: 03b27bdcb7c3
Create Date: 2020-07-21 09:37:35.995604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd90bf7b5d206'
down_revision = '03b27bdcb7c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event_rsvp',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('checked_in', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('event_rsvp')
    # ### end Alembic commands ###
