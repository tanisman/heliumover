"""Initial migration.

Revision ID: f493cfdd4108
Revises: 
Create Date: 2022-06-10 04:27:37.326835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f493cfdd4108'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('proxy_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('hotspot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=128), nullable=False),
    sa.Column('registered_on', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['proxy_group.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address')
    )
    op.create_table('rxpk',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('poc_id', sa.String(length=128), nullable=False),
    sa.Column('payload', sa.String(length=540), nullable=False),
    sa.Column('receiver_lat', sa.Float(precision=53), nullable=False),
    sa.Column('receiver_lng', sa.Float(precision=53), nullable=False),
    sa.Column('receiver_address', sa.String(length=128), nullable=False),
    sa.Column('receiver_gain', sa.Integer(), nullable=False),
    sa.Column('received_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['proxy_group.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('poc_id')
    )
    op.create_table('txpk',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('poc_id', sa.String(length=128), nullable=False),
    sa.Column('payload', sa.String(length=540), nullable=False),
    sa.Column('transmitter_lat', sa.Float(precision=53), nullable=False),
    sa.Column('transmitter_lng', sa.Float(precision=53), nullable=False),
    sa.Column('transmitter_address', sa.String(length=128), nullable=False),
    sa.Column('transmitted_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['proxy_group.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('poc_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('txpk')
    op.drop_table('rxpk')
    op.drop_table('hotspot')
    op.drop_table('proxy_group')
    # ### end Alembic commands ###
