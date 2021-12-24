"""empty message

Revision ID: 03802ed8b5c2
Revises: a8cb483462c9
Create Date: 2020-07-29 18:46:39.725694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03802ed8b5c2'
down_revision = 'a8cb483462c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mentor_profile', sa.Column('linked_in', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mentor_profile', 'linked_in')
    # ### end Alembic commands ###
