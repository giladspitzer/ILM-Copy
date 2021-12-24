"""empty message

Revision ID: dc0c4b0b605e
Revises: 368482e8d28b
Create Date: 2020-08-17 11:12:01.061225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc0c4b0b605e'
down_revision = '368482e8d28b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('intended_mentor', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'intended_mentor')
    # ### end Alembic commands ###