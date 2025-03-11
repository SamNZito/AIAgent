"""Initial migration

Revision ID: 116e5d4d606c
Revises: 
Create Date: 2025-02-25 15:08:09.897712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '116e5d4d606c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('job_role', sa.String(length=100), nullable=False),
    sa.Column('industry', sa.String(length=100), nullable=False),
    sa.Column('location', sa.String(length=200), nullable=False),
    sa.Column('work_type', sa.String(length=50), nullable=False),
    sa.Column('position_level', sa.String(length=50), nullable=False),
    sa.Column('salary', sa.String(length=50), nullable=True),
    sa.Column('target_company', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('project')
    op.drop_table('user')
    # ### end Alembic commands ###
