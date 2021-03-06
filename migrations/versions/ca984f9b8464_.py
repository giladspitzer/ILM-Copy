"""empty message

Revision ID: ca984f9b8464
Revises: dfc06ce82de8
Create Date: 2020-07-29 12:06:47.797626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca984f9b8464'
down_revision = 'dfc06ce82de8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mentor_profile', sa.Column('zoom_link', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mentor_profile', 'zoom_link')
    # ### end Alembic commands ###
