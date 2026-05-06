"""Add users table for authentication

Revision ID: 002_add_users
Revises: 001_init
Create Date: 2026-05-05

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_add_users'
down_revision = '001_init'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Add user_id foreign key to resumes table
    op.add_column('resumes', sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True))
    op.create_index('ix_resumes_user_id', 'resumes', ['user_id'])
    
    # Add user_id to applications
    op.add_column('applications', sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True))
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_applications_user_id')
    op.drop_column('applications', 'user_id')
    
    op.drop_index('ix_resumes_user_id')
    op.drop_column('resumes', 'user_id')
    
    op.drop_index('ix_users_email')
    op.drop_table('users')
