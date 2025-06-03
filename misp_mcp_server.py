#!/usr/bin/env python3
"""
MISP MCP Server - Expose MISP IOC functions via MCP
Simple fastmcp 2.0 implementation
"""

import json
import os
from typing import List, Dict, Any
from fastmcp import FastMCP
from dotenv import load_dotenv

# Import your existing MISP functions
from misp_to_json import (
    get_misp_key,
    get_last24h_iocs,
    filter_results,
)

# Load environment variables
load_dotenv()

# Create the MCP server
mcp = FastMCP("MISP IOC Server")

@mcp.tool()
def get_recent_iocs() -> List[Dict[str, Any]]:
    """
    Get IOCs from MISP that were added in the last 24 hours.
    
    Returns:
        List of IOC dictionaries with filtered fields
    """
    try:
        # Get raw IOCs from MISP
        raw_iocs = get_last24h_iocs()
        
        if not raw_iocs:
            return []
        
        # Filter and clean the results
        filtered_iocs = filter_results(raw_iocs)
        
        return filtered_iocs
        
    except Exception as e:
        raise Exception(f"Failed to retrieve IOCs: {str(e)}")

@mcp.tool()
def get_ioc_summary() -> Dict[str, Any]:
    """
    Get a summary of recent IOCs including counts by type.
    
    Returns:
        Dictionary containing IOC summary statistics
    """
    try:
        # Get filtered IOCs
        iocs = get_recent_iocs()
        
        if not iocs:
            return {
                "total_count": 0,
                "type_counts": {},
                "message": "No IOCs found in last 24 hours"
            }
        
        # Count by type
        type_counts = {}
        for ioc in iocs:
            ioc_type = ioc.get('type', 'unknown')
            type_counts[ioc_type] = type_counts.get(ioc_type, 0) + 1
        
        # Get sample IOCs (first 5)
        sample_iocs = []
        for ioc in iocs[:5]:
            sample_iocs.append({
                'type': ioc.get('type', 'unknown'),
                'value': ioc.get('value', 'N/A'),
                'event': ioc.get('event', '')
            })
        
        return {
            "total_count": len(iocs),
            "type_counts": type_counts,
            "sample_iocs": sample_iocs,
            "message": f"Found {len(iocs)} IOCs in last 24 hours"
        }
        
    except Exception as e:
        raise Exception(f"Failed to get IOC summary: {str(e)}")

@mcp.tool()
def get_iocs_by_type(ioc_type: str) -> List[Dict[str, Any]]:
    """
    Get IOCs filtered by a specific type.
    
    Args:
        ioc_type: The type of IOC to filter for (e.g., 'ip-dst', 'domain', 'url')
    
    Returns:
        List of IOCs matching the specified type
    """
    try:
        # Get all recent IOCs
        all_iocs = get_recent_iocs()
        
        # Filter by type
        filtered_iocs = [
            ioc for ioc in all_iocs 
            if ioc.get('type', '').lower() == ioc_type.lower()
        ]
        
        return filtered_iocs
        
    except Exception as e:
        raise Exception(f"Failed to get IOCs by type: {str(e)}")

@mcp.tool()
def save_iocs_to_file(filename: str = None) -> Dict[str, str]:
    """
    Save recent IOCs to a JSON file.
    
    Args:
        filename: Optional filename for the output file
    
    Returns:
        Dictionary with status and filename
    """
    try:
        # Get recent IOCs
        iocs = get_recent_iocs()
        
        if not iocs:
            return {
                "status": "error",
                "message": "No IOCs found to save"
            }
        
        # Generate filename if not provided
        if not filename:
            from datetime import datetime
            now = datetime.now().strftime('%Y%m%dT%H%M%S')
            filename = f'misp_iocs_last24h_{now}.json'
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(iocs, f, indent=2, default=str)
        
        return {
            "status": "success",
            "message": f"Saved {len(iocs)} IOCs to {filename}",
            "filename": filename,
            "count": len(iocs)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save IOCs: {str(e)}"
        }

@mcp.tool()
def check_misp_connection() -> Dict[str, Any]:
    """
    Check if MISP connection is properly configured.
    
    Returns:
        Dictionary with connection status
    """
    try:
        # Check environment variables
        misp_url = os.getenv('MISP_URL')
        misp_key = os.getenv('MISP_API_KEY')
        
        if not misp_url:
            return {
                "status": "error",
                "message": "MISP_URL not found in environment variables"
            }
        
        if not misp_key:
            return {
                "status": "error", 
                "message": "MISP_API_KEY not found in environment variables"
            }
        
        # Try to get the API key (this validates the key exists)
        get_misp_key()
        
        return {
            "status": "success",
            "message": "MISP connection configured successfully",
            "misp_url": misp_url,
            "api_key_configured": bool(misp_key)
        }
        
    except SystemExit:
        return {
            "status": "error",
            "message": "MISP API key not configured properly"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection check failed: {str(e)}"
        }

# Add a resource to provide server information
@mcp.resource("misp://server-info")
def get_server_info() -> str:
    """
    Get information about this MISP MCP server.
    """
    info = {
        "name": "MISP IOC Server",
        "description": "MCP server for retrieving IOCs from MISP",
        "version": "1.0.0",
        "available_tools": [
            "get_recent_iocs - Get IOCs from last 24 hours",
            "get_ioc_summary - Get summary statistics of recent IOCs", 
            "get_iocs_by_type - Filter IOCs by type",
            "save_iocs_to_file - Save IOCs to JSON file",
            "check_misp_connection - Verify MISP connection"
        ]
    }
    return json.dumps(info, indent=2)

if __name__ == "__main__":
    # Run the server
    mcp.run()