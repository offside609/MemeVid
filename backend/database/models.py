"""
Database models for AI Meme Video Agent
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class VideoGeneration(Base):
    """
    Model for tracking video generation requests
    """
    __tablename__ = "video_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), unique=True, index=True)
    description = Column(Text)
    style = Column(String(50), default="funny")
    
    # Media info
    filename = Column(String(255))
    duration = Column(Integer)
    format = Column(String(10), default="mp4")
    
    # Processing status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    
    # Results
    video_url = Column(String(500))
    captions = Column(Text)  # JSON string
    storyline = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime)
    
    # Processing info
    processing_time = Column(Float)
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<VideoGeneration(id={self.id}, request_id='{self.request_id}', status='{self.status}')>"

class AgentNode(Base):
    """
    Model for tracking individual agent node executions
    """
    __tablename__ = "agent_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, index=True)
    node_name = Column(String(50))
    node_type = Column(String(50))
    
    # Execution info
    status = Column(String(20), default="pending")
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    processing_time = Column(Float)
    
    # Input/Output
    input_data = Column(Text)  # JSON string
    output_data = Column(Text)  # JSON string
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<AgentNode(id={self.id}, node_name='{self.node_name}', status='{self.status}')>"

class SystemMetrics(Base):
    """
    Model for tracking system performance metrics
    """
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    metric_name = Column(String(100))
    metric_value = Column(Float)
    metric_unit = Column(String(20))
    
    # Context
    node_name = Column(String(50))
    generation_id = Column(Integer)
    
    def __repr__(self):
        return f"<SystemMetrics(id={self.id}, metric='{self.metric_name}', value={self.metric_value})>"
