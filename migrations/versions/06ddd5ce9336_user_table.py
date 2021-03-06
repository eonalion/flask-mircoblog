"""user_table

Revision ID: 06ddd5ce9336
Revises: df6821954da7
Create Date: 2022-04-05 19:26:59.941875

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06ddd5ce9336'
down_revision = 'df6821954da7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_account', sa.Column('image', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_account', 'image')
    # ### end Alembic commands ###
