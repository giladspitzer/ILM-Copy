"""empty message

Revision ID: 0affff267cc9
Revises: ea0a73814211
Create Date: 2020-07-22 10:36:20.266226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0affff267cc9'
down_revision = 'ea0a73814211'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('speaker_profile', sa.Column('img', sa.String(length=600), nullable=True))
    op.add_column('speaker_profile', sa.Column('linkedin', sa.String(length=1000), nullable=True))
    op.add_column('speaker_profile', sa.Column('title', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('speaker_profile', 'title')
    op.drop_column('speaker_profile', 'linkedin')
    op.drop_column('speaker_profile', 'img')
    # ### end Alembic commands ###
