"""empty message

Revision ID: 03b27bdcb7c3
Revises: 
Create Date: 2020-07-21 09:07:58.929768

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '03b27bdcb7c3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('img', sa.String(length=200), nullable=True))
    op.drop_column('event', 'specific_img')
    op.drop_column('event', 'sponsor_id')
    op.drop_column('event', 'location')
    op.drop_column('event', 'virtual')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('virtual', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('event', sa.Column('location', mysql.VARCHAR(collation='utf8_unicode_ci', length=200), nullable=True))
    op.add_column('event', sa.Column('sponsor_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('event', sa.Column('specific_img', mysql.VARCHAR(collation='utf8_unicode_ci', length=200), nullable=True))
    op.drop_column('event', 'img')
    # ### end Alembic commands ###
