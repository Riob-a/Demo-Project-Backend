"""added length

Revision ID: 6619f0df1126
Revises: e955404e5ca1
Create Date: 2024-11-21 16:37:55.489458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6619f0df1126'
down_revision = 'e955404e5ca1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=80),
               type_=sa.String(length=225),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=255),
               existing_nullable=False)
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(length=500),
               existing_nullable=False)
        batch_op.alter_column('role',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=250),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.String(length=250),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=500),
               type_=sa.VARCHAR(length=128),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=120),
               existing_nullable=False)
        batch_op.alter_column('username',
               existing_type=sa.String(length=225),
               type_=sa.VARCHAR(length=80),
               existing_nullable=False)

    # ### end Alembic commands ###