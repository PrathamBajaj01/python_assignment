# app/config.py
"""
Central application configuration for both Flask and PynamoDB models.
Loads values from environment variables (set by Serverless in Lambda),
and provides a Config class + helper for PynamoDB Meta blocks.
"""

import os
from typing import Optional, Dict, Any


class Config:
    """
    Main configuration class used by the Flask app and PynamoDB models.
    """

    # Region — defaults to us-east-1
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # Optional local DynamoDB endpoint (e.g., http://localhost:8000 for DynamoDB Local)
    DYNAMODB_ENDPOINT: Optional[str] = os.getenv("DYNAMODB_ENDPOINT")

    # Logging level with safe fallback
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def pynamodb_meta_for(table_name: str) -> Dict[str, Any]:
        """
        Returns dictionary used in PynamoDB model Meta classes.
        Example usage:
            class Meta:
                **Config.pynamodb_meta_for("Customers")
        """
        meta: Dict[str, Any] = {
            "table_name": table_name,
            "region": Config.AWS_REGION,
        }

        # Add local endpoint if provided
        if Config.DYNAMODB_ENDPOINT:
            meta["host"] = Config.DYNAMODB_ENDPOINT

        return meta
