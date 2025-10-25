"""
Unit tests for agent nodes
"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from backend.nodes.base_node import BaseNode
from backend.nodes.ingest_node import IngestNode
from backend.nodes.perception_node import PerceptionNode


class TestBaseNode:
    """Test base node functionality"""

    def test_base_node_initialization(self):
        """Test base node initialization"""

        # Create a concrete implementation for testing
        class TestNode(BaseNode):
            async def process(self, input_data):
                return {"result": "test"}

        node = TestNode("test_node", timeout=30)
        assert node.name == "test_node"
        assert node.timeout == 30
        assert node.logger is not None

    def test_base_node_str(self):
        """Test base node string representation"""

        # Create a concrete implementation for testing
        class TestNode(BaseNode):
            async def process(self, input_data):
                return {"result": "test"}

        node = TestNode("test_node")
        assert "test_node" in str(node)
        assert "TestNode" in str(node)

    @pytest.mark.asyncio
    async def test_base_node_timeout(self):
        """Test base node timeout handling"""

        class SlowNode(BaseNode):
            async def process(self, input_data):
                await asyncio.sleep(2)  # Longer than timeout
                return {"result": "done"}

        node = SlowNode("slow_node", timeout=1)
        result = await node.run({"test": "data"})

        assert result["success"] is False
        assert result["error"] == "Timeout"
        assert result["node_name"] == "slow_node"

    @pytest.mark.asyncio
    async def test_base_node_error_handling(self):
        """Test base node error handling"""

        class ErrorNode(BaseNode):
            async def process(self, input_data):
                raise ValueError("Test error")

        node = ErrorNode("error_node")
        result = await node.run({"test": "data"})

        assert result["success"] is False
        assert "Test error" in result["error"]
        assert result["node_name"] == "error_node"


class TestIngestNode:
    """Test ingest node functionality"""

    def test_ingest_node_initialization(self):
        """Test ingest node initialization"""
        node = IngestNode()
        assert node.name == "ingest"
        assert node.timeout == 60

    @pytest.mark.asyncio
    async def test_ingest_node_process(self, sample_agent_node_input):
        """Test ingest node processing"""
        node = IngestNode()
        result = await node.process(sample_agent_node_input)

        assert "media_info" in result
        assert "status" in result
        assert "ready_for_processing" in result
        assert result["status"] == "ingested"
        assert result["ready_for_processing"] is True

    @pytest.mark.asyncio
    async def test_ingest_node_run(self, sample_agent_node_input):
        """Test ingest node run method"""
        node = IngestNode()
        result = await node.run(sample_agent_node_input)

        assert result["success"] is True
        assert result["node_name"] == "ingest"
        assert "processing_time" in result
        assert "data" in result
        assert result["data"]["status"] == "ingested"


class TestPerceptionNode:
    """Test perception node functionality"""

    def test_perception_node_initialization(self):
        """Test perception node initialization"""
        node = PerceptionNode()
        assert node.name == "perception"
        assert node.timeout == 120

    @pytest.mark.asyncio
    async def test_perception_node_process(self, sample_agent_node_input):
        """Test perception node processing"""
        node = PerceptionNode()

        # Add media_info to input (as would come from ingest node)
        input_data = sample_agent_node_input.copy()
        input_data["media_info"] = {
            "filename": "test.mp4",
            "duration": 30,
            "format": "mp4",
        }

        result = await node.process(input_data)

        assert "analysis" in result
        assert "confidence" in result
        assert "processing_notes" in result
        assert result["confidence"] == 0.85
        assert "scenes" in result["analysis"]
        assert "objects" in result["analysis"]
        assert "emotions" in result["analysis"]

    @pytest.mark.asyncio
    async def test_perception_node_run(self, sample_agent_node_input):
        """Test perception node run method"""
        node = PerceptionNode()

        input_data = sample_agent_node_input.copy()
        input_data["media_info"] = {"filename": "test.mp4", "duration": 30}

        result = await node.run(input_data)

        assert result["success"] is True
        assert result["node_name"] == "perception"
        assert "processing_time" in result
        assert "data" in result
        assert "analysis" in result["data"]


class TestNodeIntegration:
    """Test node integration scenarios"""

    @pytest.mark.asyncio
    async def test_ingest_to_perception_flow(self, sample_agent_node_input):
        """Test flow from ingest to perception node"""
        # Run ingest node
        ingest_node = IngestNode()
        ingest_result = await ingest_node.run(sample_agent_node_input)

        assert ingest_result["success"] is True

        # Use ingest output as perception input
        perception_input = sample_agent_node_input.copy()
        perception_input["media_info"] = ingest_result["data"]["media_info"]

        perception_node = PerceptionNode()
        perception_result = await perception_node.run(perception_input)

        assert perception_result["success"] is True
        assert "analysis" in perception_result["data"]

    @pytest.mark.asyncio
    async def test_node_error_propagation(self):
        """Test that node errors are properly handled"""

        class FailingNode(BaseNode):
            async def process(self, input_data):
                raise RuntimeError("Simulated failure")

        node = FailingNode("failing_node")
        result = await node.run({"test": "data"})

        assert result["success"] is False
        assert "Simulated failure" in result["error"]
        assert result["node_name"] == "failing_node"
