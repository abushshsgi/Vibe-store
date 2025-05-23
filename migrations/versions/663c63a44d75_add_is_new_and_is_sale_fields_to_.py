"""Add is_new and is_sale fields to Product model

Revision ID: 663c63a44d75
Revises: 
Create Date: 2025-04-10 20:46:22.121826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '663c63a44d75'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_new', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('is_sale', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('is_sale')
        batch_op.drop_column('is_new')

    # ### end Alembic commands ###
