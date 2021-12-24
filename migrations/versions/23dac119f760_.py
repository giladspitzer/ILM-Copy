"""empty message

Revision ID: 23dac119f760
Revises: ca984f9b8464
Create Date: 2020-07-29 12:40:20.240305

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23dac119f760'
down_revision = 'ca984f9b8464'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mentor_profile', sa.Column('zoom_password', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mentor_profile', 'zoom_password')
    # ### end Alembic commands ###
