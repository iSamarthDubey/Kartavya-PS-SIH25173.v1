"""
Visual Response Types - Standardized format for frontend-backend communication
Matches frontend/src/types/visual.ts interface expectations
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Literal
from datetime import datetime


class VisualConfig(BaseModel):
    """Configuration for visual rendering"""
    x_field: Optional[str] = None
    y_field: Optional[str] = None
    color_field: Optional[str] = None
    size_field: Optional[str] = None
    chart_type: Optional[str] = None
    field: Optional[str] = None
    limit: Optional[int] = None
    height: Optional[int] = None
    width: Optional[int] = None
    show_legend: Optional[bool] = True
    show_grid: Optional[bool] = True
    animation: Optional[bool] = True


class VisualMetadata(BaseModel):
    """Metadata for visual payload"""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    query_type: Optional[str] = None
    data_source: Optional[str] = None
    total_records: Optional[int] = None
    processing_time_ms: Optional[float] = None
    cache_hit: Optional[bool] = None


class VisualPayload(BaseModel):
    """
    Standardized visual payload format matching frontend expectations
    This ensures frontend can render any visualization sent by backend
    """
    type: Literal[
        'chart', 'table', 'summary_card', 'network_graph', 
        'map', 'timeline', 'alert_feed', 'metric_gauge'
    ] = Field(..., description="Type of visualization")
    
    title: str = Field(..., description="Display title for the visualization")
    
    data: List[Dict[str, Any]] = Field(
        ..., 
        description="Data array for visualization"
    )
    
    config: Optional[VisualConfig] = Field(
        None,
        description="Configuration for rendering"
    )
    
    metadata: Optional[VisualMetadata] = Field(
        None,
        description="Additional metadata"
    )
    
    # Additional fields for specific visualization types
    summary: Optional[str] = Field(None, description="Text summary of the data")
    insights: Optional[List[str]] = Field(None, description="Key insights from data")


class ChartPayload(VisualPayload):
    """Specialized chart payload"""
    type: Literal['chart'] = 'chart'
    chart_type: Literal['bar', 'line', 'pie', 'area', 'scatter'] = 'bar'


class TablePayload(VisualPayload):
    """Specialized table payload"""
    type: Literal['table'] = 'table'
    columns: List[Dict[str, str]] = Field(..., description="Column definitions")
    sortable: bool = True
    searchable: bool = True
    paginated: bool = True


class SummaryCardPayload(VisualPayload):
    """Specialized summary card payload"""
    type: Literal['summary_card'] = 'summary_card'
    value: Union[str, int, float] = Field(..., description="Primary value")
    change: Optional[Dict[str, Any]] = Field(None, description="Change information")
    status: Optional[Literal['normal', 'warning', 'critical']] = 'normal'
    color: Optional[Literal['primary', 'accent', 'warning', 'danger']] = 'primary'


class NetworkGraphPayload(VisualPayload):
    """Specialized network graph payload"""
    type: Literal['network_graph'] = 'network_graph'
    nodes: List[Dict[str, Any]] = Field(..., description="Network nodes")
    edges: List[Dict[str, Any]] = Field(..., description="Network edges")


def create_chart_payload(
    title: str,
    data: List[Dict[str, Any]],
    chart_type: str = 'bar',
    x_field: str = None,
    y_field: str = None,
    **kwargs
) -> ChartPayload:
    """Helper function to create standardized chart payload"""
    config = VisualConfig(
        chart_type=chart_type,
        x_field=x_field,
        y_field=y_field,
        **kwargs
    )
    
    metadata = VisualMetadata(
        query_type=kwargs.get('query_type'),
        data_source=kwargs.get('data_source'),
        total_records=len(data)
    )
    
    return ChartPayload(
        title=title,
        data=data,
        chart_type=chart_type,
        config=config,
        metadata=metadata
    )


def create_table_payload(
    title: str,
    data: List[Dict[str, Any]],
    columns: List[Dict[str, str]] = None,
    **kwargs
) -> TablePayload:
    """Helper function to create standardized table payload"""
    # Auto-generate columns if not provided
    if not columns and data:
        columns = [
            {"key": key, "label": key.replace('_', ' ').title()}
            for key in data[0].keys()
        ]
    
    config = VisualConfig(**kwargs)
    metadata = VisualMetadata(
        query_type=kwargs.get('query_type'),
        data_source=kwargs.get('data_source'),
        total_records=len(data)
    )
    
    return TablePayload(
        title=title,
        data=data,
        columns=columns or [],
        config=config,
        metadata=metadata
    )


def create_summary_card_payload(
    title: str,
    value: Union[str, int, float],
    change: Dict[str, Any] = None,
    status: str = 'normal',
    **kwargs
) -> SummaryCardPayload:
    """Helper function to create standardized summary card payload"""
    config = VisualConfig(**kwargs)
    metadata = VisualMetadata(
        query_type=kwargs.get('query_type'),
        data_source=kwargs.get('data_source')
    )
    
    return SummaryCardPayload(
        title=title,
        data=[{"value": value}],  # Wrap value in data array for consistency
        value=value,
        change=change,
        status=status,
        config=config,
        metadata=metadata
    )
