#!/usr/bin/env python3
"""
Simple MISP IOC Retrieval Script - Get IOCs from last 24 hours
Based on working implementation pattern
"""

import json
import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from pymisp import PyMISP

# Load environment variables
load_dotenv()

# Configuration
MISP_URL = os.getenv('MISP_URL')
OUTPUT_FIELDS = ('value', 'type', 'timestamp', 'category', 'comment', 'Tag', 'Event')


def get_misp_key() -> str:
    """Get the MISP authkey from environment variables
    
    Returns
    -------
    str
        The MISP authkey
    """
    key = os.getenv('MISP_API_KEY')
    if not key:
        print('Error: MISP_API_KEY not found in environment variables.')
        print('Please create a .env file with: MISP_API_KEY=your-api-key-here')
        exit()
    return key


def get_last24h_iocs() -> List[dict]:
    """Query the MISP API for last 24 hours of IOCs
    
    Returns
    -------
    list[dict]
        A list of IOCs as dictionaries
    """
    
    # Instantiate API Object (no SSL verification for local Docker)
    try:
        misp = PyMISP(MISP_URL, get_misp_key(), ssl=False)
        print(f'Connected to MISP at {MISP_URL}')
    except Exception as e:
        print(f'Failed to connect to MISP: {e}')
        exit()

    print(f'Getting all IOCs added to MISP in past 24 hours...')

    # Query API for IOCs using the working pattern
    try:
        # Use the search method with timestamp parameter like the working example
        results = misp.search('attributes', timestamp='60d')
        
        # Handle different response formats
        if isinstance(results, dict) and 'Attribute' in results:
            iocs = results['Attribute']
        elif isinstance(results, list):
            # If results is a list of events, extract attributes
            iocs = []
            for event in results:
                if hasattr(event, 'attributes'):
                    iocs.extend([attr.to_dict() for attr in event.attributes])
                elif isinstance(event, dict) and 'Attribute' in event:
                    if isinstance(event['Attribute'], list):
                        iocs.extend(event['Attribute'])
                    else:
                        iocs.append(event['Attribute'])
        else:
            iocs = results if results else []
            
        print(f'Got {len(iocs)} IOCs from MISP')
        
    except Exception as e:
        print(f'Error while querying MISP for IOCs: {str(e)}')

    return iocs


def filter_results(iocs: List[dict]) -> List[dict]:
    """Take a list of IOC dictionaries and return a filtered list
    
    Parameters
    ----------
    iocs : list[dict]
        A list of IOCs as dictionaries
        
    Returns
    -------
    list[dict]
        A filtered list of IOCs as dictionaries
    """
    out = []
    for ioc in iocs:
        keep = {}
        for k, v in ioc.items():
            if k not in OUTPUT_FIELDS:
                continue
            else:
                if k == 'Tag':
                    # Handle tags - could be list of dicts or strings
                    if isinstance(v, list):
                        if v and isinstance(v[0], dict):
                            keep['tags'] = "|".join([tag.get('name', str(tag)) for tag in v])
                        else:
                            keep['tags'] = "|".join([str(tag) for tag in v])
                    else:
                        keep['tags'] = str(v) if v else ""
                elif k == 'Event':
                    # Handle event info
                    if isinstance(v, dict):
                        keep['event'] = v.get('info', str(v))
                    else:
                        keep['event'] = str(v) if v else ""
                else:
                    keep[k] = v
        
        # Only add IOCs that have a value
        if keep.get('value'):
            out.append(keep)
    
    return out


def ioc_dicts_to_json(iocs: List[dict], filename: str = None) -> None:
    """Take a list of ioc dictionaries and write to a JSON file.
    
    Parameters
    ----------
    iocs : List[dict]
        The indicators to be written out to a file
    filename : str, optional
        The desired name/path for the output file
    """
    if not filename:
        now = datetime.now().strftime('%Y%m%dT%H%M%S')
        filename = f'misp_iocs_last24h_{now}.json'
    
    with open(filename, 'w') as f:
        json.dump(iocs, f, indent=2, default=str)
    
    print(f'Wrote {len(iocs)} IOCs to JSON file: {filename}')


def display_iocs_summary(iocs: List[dict]) -> None:
    """Display a summary of the IOCs found"""
    if not iocs:
        print("No IOCs to display")
        return
    
    print(f"\n=== IOC Summary ({len(iocs)} total) ===")
    
    # Count by type
    type_counts = {}
    for ioc in iocs:
        ioc_type = ioc.get('type', 'unknown')
        type_counts[ioc_type] = type_counts.get(ioc_type, 0) + 1
    
    print("\nIOCs by type:")
    for ioc_type, count in sorted(type_counts.items()):
        print(f"  {ioc_type}: {count}")
    
    print(f"\nFirst 10 IOCs:")
    for i, ioc in enumerate(iocs[:10], 1):
        print(f"  {i}. {ioc.get('type', 'unknown').upper()}: {ioc.get('value', 'N/A')}")
        if ioc.get('event'):
            print(f"     Event: {ioc['event']}")


def main():
    """Main function"""
    print("MISP IOC Retrieval - Last 24 Hours")
    print("=" * 40)
    
    # Get IOCs from last 24 hours
    iocs = get_last24h_iocs()
    
    # Process results
    if not iocs:
        print('No IOCs found in last 24h. Nothing to output.')
        return
    
    # Filter and clean results
    filtered_iocs = filter_results(iocs)
    
    if not filtered_iocs:
        print('No valid IOCs after filtering. Nothing to output.')
        return
    
    # Display summary
    display_iocs_summary(filtered_iocs)
    
    # Ask user what to do with results
    print(f"\nOptions:")
    print("1. Save to JSON file")
    print("2. Display full JSON output")
    print("3. Both")
    print("4. Exit")
    
    choice = input("Choose option (1-4): ").strip()
    
    if choice in ['1', '3']:
        filename = input("Enter filename (or press Enter for auto-generated): ").strip()
        if not filename:
            filename = None
        ioc_dicts_to_json(filtered_iocs, filename)
    
    if choice in ['2', '3']:
        print("\n=== Full JSON Output ===")
        print(json.dumps(filtered_iocs, indent=2, default=str))


if __name__ == '__main__':
    main()