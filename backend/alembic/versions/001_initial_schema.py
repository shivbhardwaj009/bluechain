"""Initial schema for bluechain ocean prediction system

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-02 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'observations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('parameter', sa.String(length=64), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=32), nullable=False),
        sa.Column('time', sa.DateTime(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('depth_m', sa.Float(), default=0.0),
        sa.Column('source', sa.String(length=64), nullable=False),
        sa.Column('qc_flag', sa.Integer(), default=1),
        sa.Column('is_ocean', sa.Boolean(), default=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
    )
    op.create_index('idx_obs_param_time', 'observations', ['parameter', 'time'])
    op.create_index('idx_obs_lat_lon', 'observations', ['latitude', 'longitude'])

    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.String(length=128), unique=True, nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('severity', sa.String(length=32), nullable=False),
        sa.Column('severity_score', sa.Float(), default=0.0),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('geojson_geometry', sa.JSON(), nullable=True),
        sa.Column('ocean_basin', sa.String(length=64), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_event_type_time', 'events', ['type', 'start_time'])

    op.create_table(
        'forecasts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('parameter', sa.String(length=64), nullable=False),
        sa.Column('horizon_days', sa.Integer(), nullable=False),
        sa.Column('forecast_made_time', sa.DateTime(), nullable=True),
        sa.Column('valid_time', sa.DateTime(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('predicted_value', sa.Float(), nullable=False),
        sa.Column('uncertainty_lower', sa.Float(), nullable=True),
        sa.Column('uncertainty_upper', sa.Float(), nullable=True),
        sa.Column('baseline_value', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(length=64), nullable=False),
        sa.Column('geojson_geometry', sa.JSON(), nullable=True),
    )

    op.create_table(
        'risk_cells',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('hazard', sa.String(length=64), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('time', sa.DateTime(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('ocean_basin', sa.String(length=64), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('contributing_factors', sa.JSON(), nullable=True),
        sa.Column('geojson_geometry', sa.JSON(), nullable=True),
    )
    op.create_index('idx_risk_hazard_time', 'risk_cells', ['hazard', 'time'])

    op.create_table(
        'spill_simulations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('simulation_id', sa.String(length=64), unique=True, nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('origin_lat', sa.Float(), nullable=False),
        sa.Column('origin_lon', sa.Float(), nullable=False),
        sa.Column('volume_m3', sa.Float(), nullable=False),
        sa.Column('oil_type', sa.String(length=64), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('duration_hours', sa.Integer(), default=72),
        sa.Column('particle_count', sa.Integer(), default=150),
        sa.Column('particle_tracks', sa.JSON(), nullable=False),
        sa.Column('affected_polygon', sa.JSON(), nullable=False),
        sa.Column('area_km2', sa.Float(), default=0.0),
        sa.Column('drift_distance_km', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'ingestion_log',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source', sa.String(length=64), nullable=False),
        sa.Column('parameter', sa.String(length=64), nullable=False),
        sa.Column('records_ingested', sa.Integer(), default=0),
        sa.Column('records_rejected', sa.Integer(), default=0),
        sa.Column('status', sa.String(length=32), default='SUCCESS'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('ingestion_log')
    op.drop_table('spill_simulations')
    op.drop_table('risk_cells')
    op.drop_table('forecasts')
    op.drop_table('events')
    op.drop_table('observations')
