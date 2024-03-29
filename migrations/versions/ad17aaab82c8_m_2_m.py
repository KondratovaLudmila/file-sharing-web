"""m_2_m

Revision ID: ad17aaab82c8
Revises: d3f259919339
Create Date: 2024-02-27 16:33:22.369210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad17aaab82c8'
down_revision: Union[str, None] = 'd3f259919339'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('note_m2m_tag', 'image_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('note_m2m_tag', 'tag_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('note_m2m_tag', 'id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('note_m2m_tag', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.alter_column('note_m2m_tag', 'tag_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('note_m2m_tag', 'image_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
