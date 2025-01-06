"""Add artworklike table

Revision ID: 4d1784ecb956
Revises: ffb6336c6d94
Create Date: 2025-01-02 20:07:51.540692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d1784ecb956'
down_revision = 'ffb6336c6d94'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artwork_likes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artwork_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artwork_id'], ['art.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('artwork_likes')
    # ### end Alembic commands ###