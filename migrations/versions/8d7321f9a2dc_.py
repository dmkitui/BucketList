"""empty message

Revision ID: 8d7321f9a2dc
Revises: e053904c6eef
Create Date: 2017-06-18 15:17:41.543372

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d7321f9a2dc'
down_revision = 'e053904c6eef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_email', sa.String(length=256), nullable=False),
    sa.Column('user_password', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_email')
    )
    op.add_column('bucket_list', sa.Column('created_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'bucket_list', 'users', ['created_by'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bucket_list', type_='foreignkey')
    op.drop_column('bucket_list', 'created_by')
    op.drop_table('users')
    # ### end Alembic commands ###