"""votes table

Revision ID: 14d28cc853dc
Revises: b4bf29f2fdbf
Create Date: 2020-04-20 12:42:28.725451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14d28cc853dc'
down_revision = 'b4bf29f2fdbf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('vote',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year1', sa.Integer(), nullable=True),
    sa.Column('year2', sa.Integer(), nullable=True),
    sa.Column('answer', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vote')
    # ### end Alembic commands ###
