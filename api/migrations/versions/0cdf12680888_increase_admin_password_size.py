"""increase admin password size

Revision ID: 0cdf12680888
Revises: ce55ac1f53d8
Create Date: 2022-06-16 19:08:57.953178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cdf12680888'
down_revision = 'ce55ac1f53d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('admin_user', 'password',
               existing_type=sa.VARCHAR(length=64),
               type_=sa.String(length=256),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('admin_user', 'password',
               existing_type=sa.String(length=256),
               type_=sa.VARCHAR(length=64),
               existing_nullable=True)
    # ### end Alembic commands ###
