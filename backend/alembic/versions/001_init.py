"""Initial schema: resumes, jobs, applications

Revision ID: 001_init
Revises: 
Create Date: 2026-05-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create resumes table
    op.create_table(
        'resumes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(512), nullable=False),
        sa.Column('file_type', sa.String(10), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('parsed_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('embedding', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_resumes_created_at', 'resumes', ['created_at'])

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('job_type', sa.String(50), nullable=True),
        sa.Column('salary_min', sa.Float(), nullable=True),
        sa.Column('salary_max', sa.Float(), nullable=True),
        sa.Column('salary_currency', sa.String(10), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('skills_required', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('source_job_id', sa.String(255), nullable=True),
        sa.Column('apply_url', sa.String(1024), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('embedding', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('scraped_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_jobs_source_job_id', 'jobs', ['source', 'source_job_id'])
    op.create_index('ix_jobs_scraped_at', 'jobs', ['scraped_at'])

    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('resume_id', sa.String(36), sa.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('match_reasons', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('missing_skills', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tailored_resume', sa.Text(), nullable=True),
        sa.Column('cover_letter', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), nullable=False, server_default='pending'),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_applications_resume_id', 'applications', ['resume_id'])
    op.create_index('ix_applications_job_id', 'applications', ['job_id'])
    op.create_index('ix_applications_status', 'applications', ['status'])


def downgrade() -> None:
    op.drop_index('ix_applications_status')
    op.drop_index('ix_applications_job_id')
    op.drop_index('ix_applications_resume_id')
    op.drop_table('applications')
    
    op.drop_index('ix_jobs_scraped_at')
    op.drop_index('ix_jobs_source_job_id')
    op.drop_table('jobs')
    
    op.drop_index('ix_resumes_created_at')
    op.drop_table('resumes')
