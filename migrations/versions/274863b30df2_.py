"""empty message

Revision ID: 274863b30df2
Revises: bb74f39985f7
Create Date: 2020-08-10 12:19:03.278553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '274863b30df2'
down_revision = 'bb74f39985f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recruiting_profile', sa.Column('linked_in', sa.String(length=340), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recruiting_profile', 'linked_in')
    # ### end Alembic commands ###
