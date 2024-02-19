"""comments

Revision ID: 80f85d2a898c
Revises: 5cc06c832caf
Create Date: 2024-02-19 02:13:48.172849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80f85d2a898c'
down_revision: Union[str, None] = '5cc06c832caf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('body', sa.Text(), nullable=False))
    op.add_column('comments', sa.Column('image_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'comments', 'images', ['image_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.drop_column('comments', 'image_id')
    op.drop_column('comments', 'body')
    # ### end Alembic commands ###