"""Change User model

Revision ID: 2bfdc0a76ce7
Revises: 5f7d466187e6
Create Date: 2024-02-17 12:19:04.120072

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2bfdc0a76ce7'
down_revision: Union[str, None] = '5f7d466187e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles')
    op.add_column('users', sa.Column('username', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('email', sa.String(length=150), nullable=False))
    op.add_column('users', sa.Column('password', sa.String(length=255), nullable=False))
    op.add_column('users', sa.Column('avatar', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('refresh_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('ban', sa.Boolean(), nullable=True))
    op.create_unique_constraint(None, 'users', ['email'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'ban')
    op.drop_column('users', 'confirmed')
    op.drop_column('users', 'refresh_token')
    op.drop_column('users', 'avatar')
    op.drop_column('users', 'password')
    op.drop_column('users', 'email')
    op.drop_column('users', 'username')
    op.create_table('roles',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='roles_pkey')
    )
    # ### end Alembic commands ###
