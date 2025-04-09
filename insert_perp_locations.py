#!/usr/bin/env python3

import os
import sys
import csv
import argparse
from datetime import datetime, UTC
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional, Tuple, Dict
import re

# Load environment variables from .env.local
load_dotenv('.env.local')

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
SCHEMA_NAME = os.getenv('NEXT_PUBLIC_DB_SCHEMA', 'dev')

# Global debug flag
DEBUG = False
# Global timestamp for all inserts
date_now = None
date_now_date_only = None

def debug(message: str) -> None:
    """Print debug message if debug mode is enabled."""
    if DEBUG:
        print(f"[DEBUG] {message}", file=sys.stderr)

# Validate required environment variables
if not SUPABASE_URL:
    print("Error: NEXT_PUBLIC_SUPABASE_URL is not set in .env.local", file=sys.stderr)
    sys.exit(1)
if not SUPABASE_KEY:
    print("Error: NEXT_PUBLIC_SUPABASE_ANON_KEY is not set in .env.local", file=sys.stderr)
    sys.exit(1)

# Initialize Supabase client
try:
    supabase: Client = create_client(
        SUPABASE_URL, 
        SUPABASE_KEY
    )
    # Set the schema through headers
    supabase.postgrest.auth(SUPABASE_KEY)
    supabase.postgrest.schema(SCHEMA_NAME)
    debug("Supabase client initialized successfully")
except Exception as e:
    print(f"Error initializing Supabase client: {str(e)}", file=sys.stderr)
    sys.exit(1)

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

# Cache for location lookups
location_cache: Dict[Tuple[str, str, str], str] = {}
# Cache for perp lookups - None means not found
perp_cache: Dict[str, Optional[str]] = {}

def load_location_cache() -> None:
    """Load all locations into the cache using the get_locations function."""
    global location_cache
    
    try:
        debug("Loading location cache from database...")
        result = supabase.rpc('get_locations', params={}).execute()
        if result.data:
            debug(f"Found {len(result.data)} locations in database")
            for row in result.data:
                key = (row['country_name'], row['state_name'], row['location_name'])
                location_cache[key] = row['location_recid']
            debug("Location cache loaded successfully")
        else:
            debug("No locations found in database")
    except Exception as e:
        print(f"Error loading location cache: {str(e)}", file=sys.stderr)
        sys.exit(1)

def get_location_recid(country: str, state: str, location: str) -> Optional[str]:
    """Get location_recid from cache."""
    key = (country, state, location)
    recid = location_cache.get(key)
    if DEBUG:
        if recid:
            debug(f"Found location_recid {recid} for {country}/{state}/{location}")
        else:
            debug(f"No location_recid found for {country}/{state}/{location}")
    return recid

def parse_date_range(year_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse year string into start and end years."""
    if '-' in year_str:
        start_year, end_year = map(int, year_str.split('-'))
        debug(f"Parsed year range: {start_year}-{end_year}")
        return start_year, end_year
    year = int(year_str)
    debug(f"Parsed single year: {year}")
    return year, None

def parse_month_range(month_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse month string into start and end month numbers."""
    if '-' in month_str:
        start_month, end_month = month_str.split('-')
        start_num = MONTH_MAP.get(start_month)
        end_num = MONTH_MAP.get(end_month)
        debug(f"Parsed month range: {start_month}({start_num})-{end_month}({end_num})")
        return start_num, end_num
    month_num = MONTH_MAP.get(month_str)
    debug(f"Parsed single month: {month_str}({month_num})")
    return month_num, None

def parse_season_range(season_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse season string into start and end month numbers."""
    if '-' in season_str:
        start_season, end_season = season_str.split('-')
        start_range = SEASON_MAP.get(start_season)
        end_range = SEASON_MAP.get(end_season)
        if start_range and end_range:
            debug(f"Parsed season range: {start_season}({start_range[0]})-{end_season}({end_range[1]})")
            return start_range[0], end_range[1]
    else:
        season_range = SEASON_MAP.get(season_str)
        if season_range:
            debug(f"Parsed single season: {season_str}({season_range[0]}-{season_range[1]})")
            return season_range[0], season_range[1]
    debug(f"Could not parse season: {season_str}")
    return None, None

def process_dates(year: str, start_date: str, end_date: str, month: str) -> Tuple[Optional[str], Optional[str]]:
    """Process date fields to determine start_date and end_date."""
    start_year, end_year = parse_date_range(year)
    
    # If year is a range, use it directly
    if end_year:
        debug(f"Using year range for dates: {start_year}-01-01 to {end_year}-12-31")
        return f"{start_year}-01-01", f"{end_year}-12-31"
    
    # Process start_date and end_date if provided
    if start_date and end_date:
        try:
            start_month, start_day = map(int, start_date.split('/'))
            end_month, end_day = map(int, end_date.split('/'))
            debug(f"Using provided dates: {start_year}-{start_month:02d}-{start_day:02d} to {start_year}-{end_month:02d}-{end_day:02d}")
            return f"{start_year}-{start_month:02d}-{start_day:02d}", f"{start_year}-{end_month:02d}-{end_day:02d}"
        except ValueError:
            debug("Invalid date format in start_date/end_date")
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
                debug(f"Using month/season range: {start_date} to {end_date}")
            else:
                end_date = None
                debug(f"Using single month: {start_date}")
            return start_date, end_date
    
    # If no specific dates, use full year
    debug(f"Using full year: {start_year}-01-01 to {start_year}-12-31")
    return f"{start_year}-01-01", f"{start_year}-12-31"

def get_perp_recid(perp_name: str) -> Optional[str]:
    """Get the recid for a perp by name."""
    # Check cache first
    if perp_name in perp_cache:
        if perp_cache[perp_name] is None:
            debug(f"Perp {perp_name} previously not found in database, skipping")
            return None
        debug(f"Found perp_recid in cache: {perp_cache[perp_name]}")
        return perp_cache[perp_name]
        
    try:
        debug(f"Looking up perp: {perp_name} - schema: {SCHEMA_NAME}")
        # Remove schema prefix from table name as it's handled by the connection
        result = supabase.table('perp').select('recid').eq('name', perp_name).execute()
        if result.data:
            perp_recid = result.data[0]['recid']
            # Add to cache
            perp_cache[perp_name] = perp_recid
            debug(f"Found perp_recid: {perp_recid}")
            return perp_recid
        else:
            # Add to cache as not found
            perp_cache[perp_name] = None
            debug(f"No perp_recid found for {perp_name}, will skip future records")
            return None
    except Exception as e:
        print(f"Error looking up perp '{perp_name}': {str(e)}", file=sys.stderr)
        return None

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
    
    # Use schema prefix in the SQL statement
    sql = f"INSERT INTO {SCHEMA_NAME}.perp_location ({', '.join(columns)}) VALUES ({', '.join(values)});"
    debug(f"Generated SQL: {sql}")
    return sql

def main():
    global DEBUG, date_now, date_now_date_only
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process and insert perp location data')
    parser.add_argument('--insert', action='store_true', help='Execute the insert statements instead of just printing them')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    DEBUG = args.debug
    debug("Debug mode enabled")
    debug("Schema name: " + SCHEMA_NAME)
    
    # Initialize date_now
    date_now = datetime.now(UTC).isoformat()
    date_now_date_only = date_now.split('T')[0]  # Keep only the date part
    debug(f"Initialized date_now: {date_now}")
    debug(f"Using date_only: {date_now_date_only}")
    
    # Load location cache
    load_location_cache()
    
    # Read from stdin
    debug("Reading input from stdin...")
    reader = csv.DictReader(sys.stdin, delimiter='|')
    
    for row in reader:
        debug(f"\nProcessing record: {row['Perp Name']} at {row['Location']}")
        
        # Skip non-MATCHED records
        if row['Status'] != 'MATCHED':
            debug(f"Skipping non-MATCHED record: Status={row['Status']}")
            continue
            
        # Get perp_recid
        perp_recid = get_perp_recid(row['Perp Name'])
        if not perp_recid:
            # Only print warning if this is the first time we see this perp
            if row['Perp Name'] not in perp_cache:
                print(f"Warning: Perp '{row['Perp Name']}' not found in database, will skip future records", file=sys.stderr)
            continue
            
        # Get location_recid from cache
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
            debug(f"Processing dates - Year: {row['Year']}, Start: {row['Start Date']}, End: {row['End Date']}, Month: {row['Month']}")
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
                'changed_by': 'script',
                'created_date': date_now_date_only,
                'changed_date': date_now_date_only
            }
            debug(f"Prepared perp_location data: {perp_location_data}")
            
            if args.insert:
                # Insert perp_location record
                debug("Executing insert...")
                # Remove schema prefix from table name as it's handled by the connection
                result = supabase.table('perp_location').insert(perp_location_data).execute()
                debug(f"Inserted perp_location record for {row['Perp Name']} at {row['Location']} with created_date={date_now_date_only}")
            else:
                # Print SQL statement (default behavior)
                debug("Generating SQL statement...")
                print(format_sql_insert(perp_location_data))
            
        except Exception as e:
            print(f"Error processing record: {str(e)}", file=sys.stderr)
            continue

if __name__ == '__main__':
    main()
