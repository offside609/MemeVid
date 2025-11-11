"""Base node class for AI agent nodes.

This module provides the abstract base class for all agent nodes
in the AI Meme Video Agent workflow.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BaseNode(ABC):
    """Base class for all AI agent nodes.

    This abstract base class provides common functionality for all agent nodes
    including logging, timeout handling, and error management.
    """

    def __init__(self, name: str, timeout: int = 30):
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"node.{name}")

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return output
        Must be implemented by subclasses
        """
        pass

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the node with timeout and error handling
        """
        try:
            self.logger.info(f"Starting {self.name} node")
            start_time = datetime.now()

            # Run with timeout
            result = await asyncio.wait_for(
                self.process(input_data), timeout=self.timeout
            )

            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            self.logger.info(f"Completed {self.name} node in {processing_time:.2f}s")

            return {
                "success": True,
                "node_name": self.name,
                "processing_time": processing_time,
                "data": result,
            }

        except asyncio.TimeoutError:
            self.logger.error(f"{self.name} node timed out after {self.timeout}s")
            return {
                "success": False,
                "node_name": self.name,
                "error": "Timeout",
                "data": None,
            }

        except Exception as e:
            self.logger.error(f"{self.name} node failed: {str(e)}")
            return {
                "success": False,
                "node_name": self.name,
                "error": str(e),
                "data": None,
            }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
