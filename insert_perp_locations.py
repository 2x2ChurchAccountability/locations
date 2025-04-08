#!/usr/bin/env python3

import os
import sys
import csv
import argparse
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional, Tuple
import re

# Load environment variables from .env.local
load_dotenv('.env.local')

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SCHEMA_NAME = os.getenv('SUPABASE_SCHEMA', 'dev')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Month name to number mapping
MONTH_MAP = {
    'Jan': 1, 'January': 1,
    'Feb': 2, 'February': 2,
    'Mar': 3, 'March': 3,
    'Apr': 4, 'April': 4,
    'May': 5,
    'Jun': 6, 'June': 6,
    'Jul': 7, 'July': 7,
    'Aug': 8, 'August': 8,
    'Sep': 9, 'September': 9,
    'Oct': 10, 'October': 10,
    'Nov': 11, 'November': 11,
    'Dec': 12, 'December': 12
}

# Season to month range mapping
SEASON_MAP = {
    'Spring': (3, 5),  # March to May
    'Summer': (6, 8),  # June to August
    'Autumn': (9, 11), # September to November
    'Fall': (9, 11),   # Alternative for Autumn
    'Winter': (12, 2)  # December to February
}

def parse_date_range(year_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse year string into start and end years."""
    if '-' in year_str:
        start_year, end_year = map(int, year_str.split('-'))
        return start_year, end_year
    return int(year_str), None

def parse_month_range(month_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse month string into start and end month numbers."""
    if '-' in month_str:
        start_month, end_month = month_str.split('-')
        return MONTH_MAP.get(start_month), MONTH_MAP.get(end_month)
    return MONTH_MAP.get(month_str), None

def parse_season_range(season_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse season string into start and end month numbers."""
    if '-' in season_str:
        start_season, end_season = season_str.split('-')
        start_range = SEASON_MAP.get(start_season)
        end_range = SEASON_MAP.get(end_season)
        if start_range and end_range:
            return start_range[0], end_range[1]
    else:
        season_range = SEASON_MAP.get(season_str)
        if season_range:
            return season_range[0], season_range[1]
    return None, None

def process_dates(year: str, start_date: str, end_date: str, month: str) -> Tuple[Optional[str], Optional[str]]:
    """Process date fields to determine start_date and end_date."""
    start_year, end_year = parse_date_range(year)
    
    # If year is a range, use it directly
    if end_year:
        return f"{start_year}-01-01", f"{end_year}-12-31"
    
    # Process start_date and end_date if provided
    if start_date and end_date:
        try:
            start_month, start_day = map(int, start_date.split('/'))
            end_month, end_day = map(int, end_date.split('/'))
            return f"{start_year}-{start_month:02d}-{start_day:02d}", f"{start_year}-{end_month:02d}-{end_day:02d}"
        except ValueError:
            pass
    
    # Process month if provided
    if month:
        # Check if it's a season
        if month in SEASON_MAP or ('-' in month and all(s in SEASON_MAP for s in month.split('-'))):
            start_month, end_month = parse_season_range(month)
        else:
            start_month, end_month = parse_month_range(month)
            
        if start_month:
            start_date = f"{start_year}-{start_month:02d}-01"
            if end_month:
                # Handle year wrap-around for seasons like Winter (Dec-Feb)
                if end_month < start_month:
                    end_year = start_year + 1
                else:
                    end_year = start_year
                end_date = f"{end_year}-{end_month:02d}-28"  # Using 28 to be safe
            else:
                end_date = None
            return start_date, end_date
    
    # If no specific dates, use full year
    return f"{start_year}-01-01", f"{start_year}-12-31"

def get_location_recid(country: str, state: str, location: str) -> Optional[str]:
    """Get location_recid using the Supabase function."""
    result = supabase.rpc(
        'get_location_recid',
        {
            'p_country_name': country,
            'p_state_name': state,
            'p_location_name': location
        }
    ).execute()
    
    return result.data if result.data else None

def get_perp_recid(perp_name: str) -> Optional[str]:
    """Get the recid for a perp by name."""
    result = supabase.table(f'{SCHEMA_NAME}.perp').select('recid').eq('name', perp_name).execute()
    return result.data[0]['recid'] if result.data else None

def format_sql_insert(perp_location_data: dict) -> str:
    """Format the insert data as a SQL statement."""
    columns = []
    values = []
    
    for key, value in perp_location_data.items():
        if value is not None:
            columns.append(key)
            if isinstance(value, str):
                values.append(f"'{value}'")
            else:
                values.append(str(value))
    
    return f"INSERT INTO {SCHEMA_NAME}.perp_location ({', '.join(columns)}) VALUES ({', '.join(values)});"

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process and insert perp location data')
    parser.add_argument('--insert', action='store_true', help='Execute the insert statements instead of just printing them')
    args = parser.parse_args()
    
    # Read from stdin
    reader = csv.DictReader(sys.stdin, delimiter='|')
    
    for row in reader:
        # Skip non-MATCHED records
        if row['Status'] != 'MATCHED':
            continue
            
        # Get perp_recid
        perp_recid = get_perp_recid(row['Perp Name'])
        if not perp_recid:
            print(f"Warning: Perp '{row['Perp Name']}' not found in database", file=sys.stderr)
            continue
            
        # Get location_recid using the function
        location_recid = get_location_recid(
            row['Country'],
            row['State'],
            row['Location']
        )
        
        if not location_recid:
            print(f"Warning: Location not found for {row['Country']}/{row['State']}/{row['Location']}", file=sys.stderr)
            continue
            
        try:
            # Process dates
            start_date, end_date = process_dates(
                row['Year'],
                row['Start Date'],
                row['End Date'],
                row['Month']
            )
            
            # Prepare perp_location data
            perp_location_data = {
                'perp_recid': perp_recid,
                'location_recid': location_recid,
                'start_date': start_date,
                'end_date': end_date,
                'note': row['Note'] if row['Note'] else None,
                'created_by': 'script',
                'changed_by': 'script'
            }
            
            if args.insert:
                # Insert perp_location record
                result = supabase.table(f'{SCHEMA_NAME}.perp_location').insert(perp_location_data).execute()
                print(f"Inserted perp_location record for {row['Perp Name']} at {row['Location']}", file=sys.stderr)
            else:
                # Print SQL statement (default behavior)
                print(format_sql_insert(perp_location_data))
            
        except Exception as e:
            print(f"Error processing record: {str(e)}", file=sys.stderr)
            continue

if __name__ == '__main__':
    main()
