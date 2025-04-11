import os
import re
import argparse
from datetime import datetime
import sys
import time
from dotenv import load_dotenv
from typing import Optional, Tuple, Dict, List
from countries_data import countries

# Global variable for validation mode
validate_mode = False

# Global variable for perp name
perp_name = ''

# Month name to number mapping
MONTH_MAP = {
    'Jan': '01', 'January': '01',
    'Feb': '02', 'February': '02',
    'Mar': '03', 'March': '03',
    'Apr': '04', 'April': '04',
    'May': '05',
    'Jun': '06', 'June': '06',
    'Jul': '07', 'July': '07',
    'Aug': '08', 'August': '08',
    'Sep': '09', 'Sept': '09', 'September': '09',
    'Oct': '10', 'October': '10',
    'Nov': '11', 'November': '11',
    'Dec': '12', 'December': '12'
}

def get_perp_home_country() -> str:
    """Determine the home country of the current perp based on their name.
    Returns a string with the country name or None if not found."""
    global perp_name
    
    # Dictionary mapping perp names to their home countries
    perp_home_countries = {
        'Marion Crawford': 'Canada',
        'Robert Flippo': 'United States',
        'Leslie White': 'United States',
        'Robert Corfield': 'Canada',
        'John Van Den Berg': 'United States',
        'Dean Bruer': 'United States',
        'Luther Raine': 'United States',
        'Mark Huddle': 'United States',
        'Jack Reddekopp': 'Canada',
        'Albert Clark': 'Canada',
        'Brad Holman': 'United States',
        'Michael Payne': 'United States'
        # Add more mappings as needed
    }

    home =perp_home_countries.get(perp_name)
    if not home:
        home = "--United States--" # This is just for unit testing
    
    return home

def print_debug(*args, **kwargs):
    """Print debug information only when in validate mode."""
    if validate_mode:
        print(*args, **kwargs)

# Load environment variables
load_dotenv('.env.local')

# Initialize Supabase client
# supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
# supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
# schema = os.getenv('NEXT_PUBLIC_DB_SCHEMA', 'dev')

# if not supabase_url or not supabase_key:
#     raise ValueError("Missing required environment variables. Please check your .env.local file.")

# supabase: Client = create_client(supabase_url, supabase_key)

def extract_perp_name(filename: str) -> str:
    """Extract the perp name from the filename."""
    match = re.match(r'(.+?)_from_(?:pdf|txt)\.txt$', filename)
    if match:
        return match.group(1).strip()
    return ''

def parse_year_line(line: str) -> Optional[Tuple[int, Optional[int]]]:
    """Parse a line containing year information.
    Returns a tuple of (start_year, end_year) where end_year is None for single years."""
    # Match patterns like "#### some text" or "####-#### some text"
    match = re.match(r'(\d{4})(?:-(\d{4}))?\s+.*', line)
    if match:
        start_year = int(match.group(1))
        end_year = int(match.group(2)) if match.group(2) else None
        return start_year, end_year
    return None

def parse_date_info(date_info: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse date information from parentheses into start and end dates.
    Returns a tuple of (start_date, end_date) in M/D format."""
    if not date_info:
        return None, None
        
    # Try to parse dates in various formats
    date_match = re.match(r'(\w+)\s+(\d+)(?:-(\d+))?', date_info)
    if date_match:
        month_str, start_day, end_day = date_match.groups()
        # Convert month name to number
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        month = month_map.get(month_str[:3])
        if month:
            start_day = int(start_day)
            start_date = f"{month}/{start_day}"
            if end_day:
                end_day = int(end_day)
                end_date = f"{month}/{end_day}"
            else:
                end_date = start_date
            return start_date, end_date
    return None, None

def adjust_state_and_state(line: str, countries: Dict) -> Optional[Dict]:
    """Handle photo patterns by ignoring them."""
    # Look for patterns like "state1 and state2"
    for country, info in countries.items():
        for state1 in info.get('states', []):
            for state2 in info.get('states', []):
                if state1 != state2:  # Avoid matching same state
                    pattern = f"{state1} and {state2}"
                    if pattern in line:
                        # Found a valid combination, replace it
                        new_line = line.replace(pattern, f"{state1}/{state2}")
                        return {'line': new_line}
    
    # If no valid combination found, return original line
    return {'line': line}

def clean_line(text: str) -> str:
    """Helper function to clean up a line after text removal."""
    # Remove any remaining parentheses and extra spaces
    # text = re.sub(r'\s*\([^)]*\)\s*', '', text)
     # Remove empty parentheses and extra spaces
    text = re.sub(r'\s*\(\s*\)\s*', '', text)
    # Replace "( " with "("
    text = re.sub(r'\(\s', '(', text)
    # Replace " )" with ")"
    text = re.sub(r'\s\)', ')', text)
    # Replace multiple spaces with a single space and strip
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove ", " from the front of the string if present
    text = re.sub(r'^,\s*', '', text)
    # Remove ", " from the end of the string if present
    text = re.sub(r',\s*$', '', text)
    return text

def get_state_country(line: str, countries: Dict) -> Optional[Dict]:
    """Get the state and country from the line.
    Returns a dict with country, state, and modified line, or None if no match found."""
    result = {
        'country': None,
        'state': None,
        'location': None,
        'line': line
    }
    
    # Get the adjusted line from adjust_state_and_state
    adjusted_result = adjust_state_and_state(line, countries)
    line = adjusted_result['line']

    if "Paris Tennessee" in line:
        result['country'] = 'United States'
        result['state'] = 'Tennessee'
        result['location'] = 'Paris'
        result['line'] = clean_line(line.replace("Paris Tennessee", ""))
        return result

    print_debug(f"\n\nBOB STATE COUNTRY 0.0 - Line: {line}")
    
    line = re.sub(r'\bN\.?\s+', 'North ', line)
    line = re.sub(r'\bS\.?\s+', 'South ', line)
    line = re.sub(r'\bE\.?\s+', 'East ', line)
    line = re.sub(r'\bW\.?\s+', 'West ', line)
    line = re.sub(r'\bNW\.?\s+', 'Northwest ', line)
    line = re.sub(r'\bNE\.?\s+', 'Northeast ', line)
    line = re.sub(r'\bSW\.?\s+', 'Southwest ', line)
    line = re.sub(r'\bSE\.?\s+', 'Southeast ', line)

    # First check if there's a state name in the input string
    earliest_state_pos = float('inf')
    found_state = None
    found_state_country = None
    
    for country_name, country_info in countries.items():
        # Check for exact state matches
        for state in country_info.get('states', []):
            if state and re.search(r'\b' + re.escape(state) + r'\b', line):  # Skip empty strings
                pos = line.find(state)
                if pos != -1 and pos < earliest_state_pos:
                    earliest_state_pos = pos
                    found_state = state
                    found_state_country = country_name

        # Check state variations
        if 'state_variations' in country_info:
            for variation, full_state in country_info['state_variations'].items():
                if variation and re.search(r'\b' + re.escape(variation) + r'\b', line):  # Skip empty strings
                    pos = line.find(variation)
                    if pos != -1 and pos < earliest_state_pos:
                        earliest_state_pos = pos
                        found_state = full_state
                        found_state_country = country_name

    print_debug(f"\n\nBOB SC 0.0 - found_state: {found_state}  country: {found_state_country}")

    # First check if any word in the line is a city
    words = line.split()
    for i in range(len(words)):
        # Try 5, 4, 3, 2, or 1 consecutive words (in that order)
        for word_count in range(5, 0, -1):
            if i + word_count <= len(words):
                potential_city = ' '.join(words[i:i + word_count]).rstrip(',')
                print_debug(f"BOB SC 0.1 - potential_city: |{potential_city}|") #if i==0 else None
#BOB1
                # If we found a state earlier, only check cities in that state's country
                countries_to_check = {found_state_country: countries[found_state_country]} if found_state_country else countries
                
                for country_name, country_info in countries_to_check.items():
                    if 'cities' in country_info:
                        # Check for multiple occurrences of the city by looking at the raw dictionary items
                        matching_states = []
                        for city, states in country_info['cities'].items():
                            # Split compound city names and check for exact matches
                            #city_parts = [c.strip() for c in city.split(',')]
                            if potential_city == city:
                                # Add all states for this city to matching_states
                                matching_states.extend(states)
                        
                        if matching_states:
                            print_debug(f"BOB SC 0.2 - found_state: {found_state}  |  matching_states: {matching_states}")
                            # If this city is part of a state name we found earlier, skip it
                            if found_state and potential_city in found_state:
                                continue
                            print_debug(f"BOB SC 0.21 - checking matching_states")
                            # Loop through all matching states
                            for state in matching_states:
                                print_debug(f"BOB SC 0.3 - checking state: {state}  | found_state: {found_state}")                        
                                # If we found a state earlier, only use cities that belong to that state

                                # two tests exercise this so if you touch it make sure those still work
                                # 1. Theodore Canada Convention
                                # 2. New York *Started in the work* Mountain Ranch 1
                                if state != found_state and found_state != found_state_country:
                                    continue

                                result['state'] = state
                                result['country'] = country_name
                                # Remove the state and country from the line
                                if state:  # Only remove state if it exists
                                    line = line.replace(state, '').strip()
                                line = line.replace(country_name, '').strip()
                                line = line.replace(potential_city, '').strip()
                                # Remove any state variations
                                if 'state_variations' in country_info:
                                    for variation in country_info['state_variations'].keys():
                                        line = re.sub(r'\b' + re.escape(variation) + r'\b', '', line).strip()
                                # Set location to city name
                                result['location'] = potential_city
                                # Keep the remaining text in the line field
                                result['line'] = line
                                return result

    print_debug(f"BOB SC 1.0 - Line: {line}")
    # First check for combined country names
    for country, info in countries.items():
        if '/' in country and country in line:
            result['country'] = country
            line = line.replace(country, '').strip()
            print_debug(f"BOB SC 1.1 - country: {country}  line: {line}")
            # Check for states in this country 1
            words = line.split()
            for i in range(len(words)):
                # Try 5, 4, 3, 2, or 1 consecutive words (in that order)
                for word_count in range(5, 0, -1):
                    if i + word_count <= len(words):
                        potential_state = ' '.join(words[i:i + word_count])
                        print_debug(f"BOB SC 1.2 - potential_state: {potential_state}")
                        # Check in regular states list
                        if potential_state in info.get('states', []):
                            result['state'] = potential_state
                            # Remove the state from the line
                            line = line.replace(potential_state, '').strip()
                            result['line'] = clean_line(line)
                            return result
                        # Check in state variations
                        if 'state_variations' in info:
                            for variation, full_state in info['state_variations'].items():
                                if potential_state == variation:
                                    result['state'] = full_state
                                    # Remove the variation from the line
                                    line = line.replace(variation, '').strip()
                                    result['line'] = clean_line(line)
                                    return result
            # If no state found in this country, check for states in other countries
            for other_country, other_info in countries.items():
                if other_country != country:
                    for state in other_info.get('states', []):
                        if state and state in line:  # Skip empty strings
                            result['state'] = state
                            # Remove the state and country from the line
                            line = line.replace(state, '').strip()
                            result['line'] = clean_line(line)
                            return result
            # No state found, just return the country
            line = line.replace(country, '').strip()
            result['line'] = clean_line(line)
            return result

    print_debug(f"BOB SC 2.0 - Line: {line}")
    # Then look for states in any country
    # Track the earliest position of any state match
    earliest_state_pos = float('inf')
    earliest_state = None
    earliest_country = None
    earliest_state_text = None

    for country, info in countries.items():
        # Skip combined country names
        if '/' in country:
            continue
            
        # Check for exact state matches
        for state in info.get('states', []):
            if state and re.search(r'\b' + re.escape(state) + r'\b', line):  # Skip empty strings
                pos = line.find(state)
                if pos != -1 and pos < earliest_state_pos:
                    earliest_state_pos = pos
                    earliest_state = state
                    earliest_country = country
                    earliest_state_text = state

        # Check state variations
        if 'state_variations' in info:
            for variation, full_state in info['state_variations'].items():
                if variation and re.search(r'\b' + re.escape(variation) + r'\b', line):  # Skip empty strings
                    pos = line.find(variation)
                    if pos != -1 and pos < earliest_state_pos:
                        earliest_state_pos = pos
                        earliest_state = full_state
                        earliest_country = country
                        earliest_state_text = variation

    print_debug(f"BOB SC 2.1 - earliest_state_pos: {earliest_state_pos}")
    print_debug(f"BOB SC 2.2 - earliest_state: {earliest_state}")
    print_debug(f"BOB SC 2.3 - earliest_country: {earliest_country}")
    print_debug(f"BOB SC 2.4 - earliest_state_text: {earliest_state_text}")
    print_debug(f"BOB SC 2.5 - line: {line}")
    
    # If we found a state, use the earliest one
    if earliest_state is not None:
        result['state'] = earliest_state
        result['country'] = earliest_country
        print_debug(f"BOB SC 2.52 - state: {earliest_state}")
        print_debug(f"BOB SC 2.51 - country: {earliest_country}")
        # Remove the state and country from the line
        line = line.replace(earliest_state_text, '').strip()
        print_debug(f"BOB SC 2.6 - line: {line}")
        line = line.replace(earliest_country, '').strip()
        print_debug(f"BOB SC 2.7 - line: {line}")
        result['line'] = clean_line(line)
        print_debug(f"BOB SC 2.8 - result(line): {result['line']}")
        return result

    print_debug(f"BOB SC 3.0 - Line: {line}")
    # Then look for exact country matches
    for country, info in countries.items():
        # Skip combined country names
        if '/' in country:
            continue
            
        if country in line:
            # Check if there's a prefix before the country name
            words = line.split()
            for i, word in enumerate(words):
                if word == country:
                    # Check if there's a prefix before the country name
                    if i > 0:
                        prefix = words[i-1].lower()
                        # If prefix is New, San, or Santa, check if it's part of a state name
                        if prefix in ['new', 'san', 'santa', 'north', 'south', 'west']:
                            potential_state = f"{words[i-1]} {country}"
                            # Check if this is a state in any country
                            for c, c_info in countries.items():
                                if potential_state in c_info.get('states', []):
                                    result['state'] = potential_state
                                    result['country'] = c
                                    # Remove the state from the line
                                    line = line.replace(potential_state, '').strip()
                                    result['line'] = clean_line(line)
                                    return result
                    break

            # Check for states in this country
            for state in info.get('states', []):
                if state and state in line:  # Skip empty strings
                    result['state'] = state
                    result['country'] = country
                    # Remove the state and country from the line
                    line = line.replace(state, '').strip()
                    line = line.replace(country, '').strip()
                    result['line'] = clean_line(line)
                    return result
            
            # Check state variations in this country
            if 'state_variations' in info:
                for variation, full_state in info['state_variations'].items():
                    if variation and variation in line:  # Skip empty strings
                        result['state'] = full_state
                        result['country'] = country
                        # Remove the variation and country from the line
                        line = line.replace(variation, '').strip()
                        line = line.replace(country, '').strip()
                        result['line'] = clean_line(line)
                        return result
            
            # If we found a country but no state, return the country
            result['country'] = country
            # Remove the country from the line
            line = line.replace(country, '').strip()
            result['line'] = clean_line(line)
            return result
    
    print_debug(f"BOB SC 4.0 - Line: {line}")
    # Finally look for country matches including variations
    for country, info in countries.items():
        # Skip combined country names
        if '/' in country:
            continue
            
        # Check for variations
        if 'variations' in info:
            for variation in info['variations']:
                if variation and variation in line:  # Skip empty strings
                    # Check if there's a prefix before the variation
                    words = line.split()
                    for i, word in enumerate(words):
                        if word == variation:
                            # Check if there's a prefix before the variation
                            if i > 0:
                                prefix = words[i-1].lower()
                                # If prefix is New, San, or Santa, check if it's part of a state name
                                if prefix in ['new', 'san', 'santa']:
                                    potential_state = f"{words[i-1]} {variation}"
                                    # Check if this is a state in any country
                                    for c, c_info in countries.items():
                                        if potential_state in c_info.get('states', []):
                                            result['state'] = potential_state
                                            result['country'] = c
                                            # Remove the state and country from the line
                                            line = line.replace(potential_state, '').strip()
                                            line = line.replace(c, '').strip()
                                            result['line'] = clean_line(line)
                                            return result
                            break
                    
                    result['country'] = country
                    # Remove the variation and country from the line
                    line = line.replace(variation, '').strip()
                    line = line.replace(country, '').strip()
                    result['line'] = clean_line(line)
                    return result

    print_debug(f"BOB SC 5.0 - Line: {line}")
    # If no state or country found, return the original line
    result['line'] = clean_line(line)
    return result

def handle_convention(line: str, countries: Dict) -> Optional[Dict]:
    """Handle convention patterns."""

    result = {
        'type': 'Convention',
        'country': None,
        'state': None,
        'location': None,
        'note': None,
        'month': None,
        'start_date': None,
        'end_date': None
    }

    if 'convention' not in line.lower() or 'convention photo' in line.lower():
        return None

    print_debug(f"\n\nBOB CON 0.0 - Line: {line}")

    # Special case for Australian Workers Convention
    if line.lower().startswith('australian workers convention'):
        result['note'] = 'Workers Convention'
        result['country'] = 'Australia'
        result['state'] = 'Australia'
        result['location'] = 'Australia'
        return result

    # Create patterns for all countries and US states
    country_patterns = []
    for country, info in countries.items():
        country_patterns.append(country)
        if 'variations' in info:
            country_patterns.extend(info['variations'])
    
    # Add state variations to the pattern
    state_variations = []
    if 'state_variations' in countries['United States']:
        state_variations.extend(countries['United States']['state_variations'].keys())
    if 'state_variations' in countries['Canada']:
        state_variations.extend(countries['Canada']['state_variations'].keys())
    
    country_pattern = '|'.join(country_patterns)
    us_states_pattern = '|'.join(countries['United States']['states'])
    state_variations_pattern = '|'.join(state_variations)

    # Remove USA after US states
    for state in countries['United States']['states']:
        line = re.sub(rf'\b{re.escape(state)}\s+USA\b', state, line, flags=re.IGNORECASE)

    # Remove UK after UK cities
    for city in countries['United Kingdom']['cities']:
        line = re.sub(rf'\b{re.escape(city)}\s+UK\b', city, line, flags=re.IGNORECASE)

    # remove "Sk- " from line - Special case that was messing up the output.  Redundant Saskatchewan anyway
    line = line.replace('Sk- ', '')

    print_debug(f"BOB CON 0.01 - Line: {line}")

    # Handle date or note in parentheses at the end
    date_visit_matches = re.finditer(r'\((.*?)\)', line)
    matches_list = list(date_visit_matches)
    
    date_note = None
    visit_note = None
    if len(matches_list) > 0:
        print_debug(f"BOB CON 0.02 - we have date_visit_matches")
        for match in matches_list:
            date_visit_note = match.group(1).strip()
            print_debug(f"BOB CON 0.1 - date_visit_match: {date_visit_note}")

            # Check if date_visit_note contains a month or season  JOE
            month_pattern = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b'
            season_pattern = r'\b(?:Spring|Summer|Fall|Autumn|Winter)\b'

            first_match = re.search(month_pattern, date_visit_note, re.IGNORECASE) or re.search(season_pattern, date_visit_note, re.IGNORECASE)
            range_found = False
            if first_match:
                print_debug(f"BOB CON 0.1.0 - Found first month/season pattern in: {first_match.group(0)}")
                remaining_text = date_visit_note[first_match.end():]
                second_match = re.search(month_pattern, remaining_text, re.IGNORECASE) or re.search(season_pattern, remaining_text, re.IGNORECASE)
                if second_match:
                    print_debug(f"BOB CON 0.1.1 - Found second month/season pattern in: {second_match.group(0)}")
                    result['month'] = f"{first_match.group(0)}-{second_match.group(0)}"
                    date_note = date_visit_note
                    range_found = True
            
            if not range_found and not date_note and (re.search(month_pattern, date_visit_note, re.IGNORECASE) or re.search(season_pattern, date_visit_note, re.IGNORECASE)):
                date_note = date_visit_note 
                #SUE
                # Check for second instance of month or season pattern after the first match
                line = line.replace(date_visit_note, '')
                date_pieces = date_visit_note.split()
                if len(date_pieces) == 1:
                    result['month'] = date_pieces[0]
                else:
                    result['month'] = date_pieces[0]
                    month = MONTH_MAP.get(date_pieces[0], date_pieces[0])
                    # Get start and possible end date
                    day_pieces = date_pieces[1].split('-')
                    if len(day_pieces) >= 1:
                        day = day_pieces[0].zfill(2)  # Pad day with leading zero if needed
                        result['start_date'] = f"{month}/{day}"
                        if len(day_pieces) >= 2:
                            end_day = day_pieces[1].zfill(2)  # Pad day with leading zero if needed
                            result['end_date'] = f"{month}/{end_day}"
                print_debug(f"BOB CON 0.2 - month: {result['month']}  |  start_date: {result['start_date']}  |  end_date: {result['end_date']}")
            elif not range_found:
                visit_note = date_visit_note.replace('Visiting Worker', '').strip()
                line = line.replace(date_visit_note, '')
                print_debug(f"BOB CON 0.3 - visit_note: {visit_note}")
    else:
        # No (somedate) found in the line so lets look for months and month ranges elsewhere in the line.  Can include July 1-30, July 1-August 30, etc.
        # Check for month ranges
        print_debug(f"BOB CON DATE 1.0 - Check for month ranges {line}")
        month_abbreviations = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)"

        # Single pattern with named groups to handle all cases
        date_range_pattern = re.compile(
            rf"""
            (?P<first_month>{month_abbreviations})
            (?:
                (?:
                    \s+
                    (?P<first_day>\d+)
                    (?:
                        -
                        (?:(?P<second_month_with_day>{month_abbreviations})\s*)?
                        (?P<second_day>\d+)
                    )?
                )|
                (?:
                    -
                    (?P<second_month_only>{month_abbreviations})
                )
            )?
            $
            """,
            re.IGNORECASE | re.VERBOSE
        )
        
        first_month = None
        first_day = None
        second_month = None
        second_day = None
        for match in date_range_pattern.finditer(line):
            first_month = match.group('first_month')
            first_day = match.group('first_day')
            second_month_with_day = match.group('second_month_with_day')
            second_month_only = match.group('second_month_only')
            second_day = match.group('second_day')

            print_debug(f"BOB CON DATE 1.1 - first_month: {first_month}  |  first_day: {first_day}  |  second_month_with_day: {second_month_with_day}  |  second_month_only: {second_month_only}  |  second_day: {second_day}")
        
        if first_month:
            result['month'] = first_month
            month = MONTH_MAP.get(first_month, first_month)
            if first_day:
                day = first_day.zfill(2)  # Pad day with leading zero if needed
                result['start_date'] = f"{month}/{day}"
                if second_day:
                    if second_month_with_day:
                        month = MONTH_MAP.get(second_month_with_day, second_month_with_day)
                    day = second_day.zfill(2)  # Pad day with leading zero if needed
                    result['end_date'] = f"{month}/{day}"
            else:
                if second_month_only:
                    result['month'] = first_month + '-' + second_month_only


    print_debug(f"BOB CON 0.4 - line: {line}")

    state_country_info = get_state_country(line, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    if state_country_info['location']:
        result['location'] = state_country_info['location']

    line = re.sub(r'\s+', ' ', state_country_info['line'])
    if "Convention".lower() not in line.lower():
        line = f"{line} Convention"

    print_debug(f"BOB CON 1.0 - country: {result['country']}")
    print_debug(f"BOB CON 1.1 - state: {result['state']}")
    print_debug(f"BOB CON 1.2 - location: {result['location']}")
    print_debug(f"BOB CON 1.3 - line: {line}")

    line = line.replace(',', '')

    print_debug(f"BOB CON 1.31 - line: {line}")

    
    # Remove the parentheses and their contents from the line
    line = re.sub(r'\([^)]*\)', '', line).strip()
    print_debug(f"BOB CON 1.7 - line: {line}")
    if date_note:
        line = line + ' - ' + date_note
    if visit_note:
        if visit_note == 'sent back to S. Africa from this convention':
            line = line + '. Visiting from South Africa. Sent back to S. Africa from this convention'
        else:
            # Check if visit_note is a two-character state code
            if len(visit_note) == 2:
                # Look up state abbreviation in state_variations for both US and Canada
                for country, info in countries.items():
                    if 'state_variations' in info and visit_note in info['state_variations']:
                        visit_note = info['state_variations'][visit_note]
                        break
            line = line + ". Visiting from " + visit_note
    result['note'] = line
    print_debug(f"BOB CON 1.8 - note: {result['note']}")

    result = adjust_location_result(result)

    print_debug(f"BOB CON 1.9 - country: |{result['country']}|    state: |{result['state']}|    location: |{result['location']}|")
        
    return result

def adjust_location_result(result):
    if not result['country']:
        result['country'] = get_perp_home_country()
    if not result['state']:
        result['state'] = result['country']
    if not result['location']:
        result['location'] = result['state']
    return result    

def handle_special_meeting(line: str, countries: Dict) -> Optional[Dict]:
    """Handle special meeting patterns.
    Format: YYYY-EEEE TTTT SSSS Special Meeting(s) (NNNN)
    Where:
    - YYYY is starting year
    - EEEE is optional ending year
    - TTTT is optional location (1-3 words)
    - SSSS is optional state/province/country
    - NNNN is optional date or note in parentheses
    """

    if not 'Special Meeting' in line:
        return None

    result = {
        'type': 'Special Meeting',
        'country': None,
        'state': None,
        'location': None,
        'note': None,
        'month': None,
        'start_date': None,
        'end_date': None
    }

    print_debug(f"\n\nBOB SPECIAL MEETING 0.0 - Line: {line}")

    # Special case for Gilbert Arizona
    # if 'Gilbert' in line and 'Arizona' in line and 'Special Meeting' in line:
    #     line = 'Gilbert ' + line.replace('Gilbert', '').strip()

    # Special case for Quebec and Atlantic
    if ('Quebec' in line or 'QC' in line) and 'Atlantic' in line:
        line = re.sub(r'(?:Quebec|QC).*?Atlantic', 'Quebec/Atlantic', line, flags=re.IGNORECASE)

    # Special case for Oregon/ S. Idaho
    if re.search(r'oregon\s*/\s*s\.\s*idaho\s+special\s+meeting', line.lower()):
        line = line.replace('Oregon/ S. Idaho', 'Oregon/Southern Idaho')

    # Special case for Newfoundland
    if 'Irishtown' in line and 'Special Meeting' in line:
        line = line.replace('(Irishtown)', 'Irishtown')

    print_debug(f"BOB SM 1.0 - Line: {line}")

    # Handle date or note in parentheses at the end
    date_visit_match = re.search(r'\((.*?)\)', line)
    
    date_note = None
    visit_note = None
    if date_visit_match:
        date_visit_note = date_visit_match.group(1).strip()

        # Check if date_visit_note contains a month or season
        month_pattern = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b'
        season_pattern = r'\b(?:Spring|Summer|Fall|Autumn|Winter)\b'
        
        #GOOBER
        if re.search(month_pattern, date_visit_note, re.IGNORECASE) or re.search(season_pattern, date_visit_note, re.IGNORECASE):
            date_note = date_visit_note
            date_pieces = date_visit_note.split()
            if len(date_pieces) == 1:
                result['month'] = date_pieces[0]
            else:
                result['month'] = date_pieces[0]
                # Handle month with period (e.g., "Dec.")
                result['month'] = date_pieces[0].rstrip('.')
                month = MONTH_MAP.get(result['month'], result['month'])
                # Handle day with ordinal (e.g., "19th")
                day = re.sub(r'(\d+)(?:st|nd|rd|th)', r'\1', date_pieces[1])
                day = day.zfill(2)  # Pad day with leading zero if needed
                result['start_date'] = f"{month}/{day}"
            print_debug(f"BOB SM 1.1 - month: {result['month']}  |  start_date: {result['start_date']}")
        else:
            visit_note = date_visit_note
        # Remove the parentheses and their contents from the line
        line = re.sub(r'\([^)]*\)', '', line).strip()

    print_debug(f"BOB SM 2.0 - Line: {line}")

    # Remove USA after US states
    for state in countries['United States']['states']:
        line = re.sub(rf'\b{re.escape(state)}\s+USA\b', state, line, flags=re.IGNORECASE)

    print_debug(f"BOB SM 3.0 - Line: {line}")

    # Hard-coded check for Doak's Special Meeting Shed
    doak_match = re.search(r"Doak.*?s", line)
    if doak_match:
        line = line.replace(doak_match.group(0), "Doak's")

    print_debug(f"BOB SM 4.0 - Line: {line}")

    text=line

    # First check if any word in the line is a country with no states
    words = line.split()
    for i, word in enumerate(words):
        for country, info in countries.items():
            if word == country and not info.get('states'):
                result['country'] = country

    print_debug(f"BOB SM 5.0 - country: {result['country']}")
    print_debug(f"BOB SM 5.1 - note: {result['note']}")
    print_debug(f"BOB SM 5.2 - line: {line}")

    state_country_info = get_state_country(text, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    if state_country_info['location']:
        result['location'] = state_country_info['location']

    result = adjust_location_result(result)
    
    result['note'] = state_country_info['line']
    if date_note:
        result['note'] = date_note + ' ' + result['note']
    if visit_note:
        result['note'] = result['note'] + " Visiting from " + visit_note

    return result

def upper_words(text):
    """
    Capitalizes the first letter of each word and trims leading/trailing spaces
    Args:
        text (str): The input text to capitalize
    Returns:
        str: The capitalized text with trimmed spaces
    """
    if not text:
        return ""
    # First trim the text
    text = text.strip()
    # Split into words and capitalize each word
    words = text.split()
    capitalized_words = [word.capitalize() for word in words]
    # Join words back together with spaces
    return " ".join(capitalized_words)

def handle_paren_text_patterns(in_parens):
    special_case_phrase = ''
    everything_else = in_parens
    if in_parens.lower().startswith('to '):
        special_case_phrase = 'to'
        everything_else = in_parens[3:].strip()
    if "pro tem" in everything_else.lower():
        special_case_phrase = 'to pro tem'
        everything_else = everything_else.replace('pro tem', '').strip()
    elif in_parens.lower().startswith('care of'):
        special_case_phrase = 'care of'
        everything_else = in_parens[8:].strip()
    elif in_parens.lower().startswith('helping'):
        special_case_phrase = 'helping'
        everything_else = in_parens[7:].strip()
    elif in_parens.lower().startswith('return home'):
        special_case_phrase = 'return home'
        everything_else = in_parens[11:].strip()
    elif in_parens.lower().startswith('return to '):
        special_case_phrase = 'return to'
        everything_else = in_parens[10:].strip()
    elif in_parens.lower().startswith('home visit'):
        special_case_phrase = 'home visit'
        everything_else = in_parens[10:].strip()
    elif in_parens.lower().startswith('visiting '):
        special_case_phrase = 'visiting'
        everything_else = in_parens[8:].strip()
    elif in_parens.lower().startswith('home'):
        special_case_phrase = 'home'
        everything_else = in_parens[4:].strip()
    elif in_parens.lower().startswith('field companion later'):
        special_case_phrase = 'field companion later'
        everything_else = in_parens[21:].strip()
    elif in_parens.lower().startswith('companion later'):
        special_case_phrase = 'companion later'
        everything_else = in_parens[21:].strip()
    elif in_parens.lower().startswith('new worker'):
        special_case_phrase = 'new worker'
        everything_else = in_parens[10:].strip()
    elif in_parens.lower().startswith('adjustments'):
        special_case_phrase = 'adjustments'
        everything_else = in_parens[11:].strip()
    elif 'pro tem' in in_parens.lower():
        special_case_phrase = 'pro tem'
        everything_else = everything_else.replace('pro tem', '').strip()
    elif 'and overseer' in everything_else.lower():
        special_case_phrase = 'overseer'
        everything_else = everything_else.replace('and overseer', '').strip()

    return special_case_phrase, everything_else

def format_paren_text_note(special_case_phrase, in_parens, after_parens):
    the_field = ""
    the_note = ""
    the_after = after_parens
    if special_case_phrase:
        if special_case_phrase == 'pro tem':
            the_note =  in_parens.strip() + ' pro tem'
        elif special_case_phrase == 'to pro tem':
            the_note = 'To ' + in_parens.strip() + ' pro tem'
        else:
            the_note = upper_words(special_case_phrase) 
            if in_parens.strip():
                the_note += ' ' + in_parens.strip()
    else:
        if "West Africa" in in_parens or "Bolivia" in in_parens or "Peru" in in_parens or "Mexico" in in_parens:
            the_note = "Laboring in " + in_parens
        elif  "Russia" in in_parens or "Ponape" in in_parens or "France" in in_parens or "Europe" in in_parens:
            the_note = "Laboring in " + in_parens
        elif  "Ukraine" in in_parens or "Philippines" in in_parens or 'Uruguay' in in_parens:
            the_note = "Laboring in " + in_parens

        elif "Convention" in in_parens or "Address" in in_parens or "Companion Later" in in_parens or "Other Arrangements" in in_parens or "Changing Fields" in in_parens:
            the_note = in_parens
        elif "Adjustments" in in_parens:
            the_note = "Adjustments: " + in_parens
        else:
            the_field = in_parens
            the_note = in_parens
    
    if special_case_phrase == 'overseer':
        if "overseer" not in the_after.lower():
            if the_after:
                the_after += ', Overseer'
            else:
                the_after = 'Overseer'
    
    return the_field, the_note, the_after

def add_to_note_list(current_note: str, addition: str) -> str:
    """Add text to a note, handling the special case of 'Workers List:'."""
    if current_note == 'Workers List':
        return f"{current_note}: {addition}"
    new_note = current_note
    if current_note:
        new_note += ', ' + addition
    else:
        new_note = addition
    return new_note

def get_month_or_range(text):
    matched_month_range = None
    matched_month_single = None

    single_month_pattern = r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|Winter|Spring|Summer|Fall|Autumn)\b'
    range_month_pattern = r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|Winter|Spring|Summer|Fall|Autumn)\s*-\s*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|Winter|Spring|Summer|Fall|Autumn)\b'

    range_month_match = re.match(range_month_pattern, text, flags=re.IGNORECASE)
    if range_month_match:
        matched_month_range = range_month_match.group(0).strip()
    else:
        single_month_match = re.match(single_month_pattern, text, flags=re.IGNORECASE)
        if single_month_match:
            matched_month_single = single_month_match.group(0).strip()

    if matched_month_range:
        return matched_month_range
    
    return matched_month_single

def handle_workers_list(line: str, countries: Dict) -> Optional[Dict]:
    """Handle workers list patterns."""
    # Only process lines that contain "workers list" or "staff'"
    if 'workers list' not in line.lower() and ('staff' not in line.lower() or 'staff photo' in line.lower()):
        return None

    # Strip workers list and staff from the line
    # line = re.sub(r'workers\s+list', '', line, flags=re.IGNORECASE).strip()
    # line = re.sub(r'staff', '', line, flags=re.IGNORECASE).strip()

    # Handle special cases where words are joined together
    line = re.sub(r'AlbertaCanada', 'Alberta Canada', line)
    line = re.sub(r'S\.Africa', 'South Africa', line)
    
    # Special case for Jan-July Workers List (Prince Albert-Big River)
    if line == "Jan-July Workers List (Prince Albert-Big River)":
        line = "Jan-July Saskatchewan Canada Workers List (Prince Albert-Big River)"
    
    # Special case for PA/ NY/New England/NJ
    if "PA/ NY/New England/NJ" in line:
        line = line.replace("PA/ NY/New England/NJ", "PA/NY/New England/NJ")

    if "CanadaWorkers" in line:
        line = line.replace("CanadaWorkers", "Canada Workers")

    if "Canada Canada" in line:
        line = line.replace("Canada Canada", "Canada")

    if "Atlantic/Quebec" in line:
        line = line.replace("Atlantic/Quebec", "Quebec/Atlantic")

    if "N.W." in line:
        line = line.replace("N.W.", "Northwest")

    if "NWOntario." in line:
        line = line.replace("NWOntario.", "Northwest Ontario")

    if "Canada Workers List (Newfoundland and Labrador) East" in line:
        line = line.replace("Canada Workers List (Newfoundland and Labrador) East", "Canada Workers List Newfoundland and Labrador (East)")
    
    if "OHio" in line:
        line = line.replace("OHio", "Ohio")

    if "Mid Island Field" in line:
        line = line.replace("Mid Island Field", "Mid Island")

    if "Assinibboia" in line:
        line = line.replace("Assinibboia", "Assiniboia")

    if "Barhead" in line:
        line = line.replace("Barhead", "Barrhead")

    if "Freeedom" in line:
        line = line.replace("Freeedom", "Freedom")

    if "North Falls Freedom" in line:
        line = line.replace("North Falls Freedom", "North Falls, Freedom")

    if "Charesholm" in line:
        line = line.replace("Charesholm", "Claresholm")

    if "PIncher" in line:
        line = line.replace("PIncher", "Pincher")

    if "Beverdam" in line:
        line = line.replace("Beverdam", "Beaver Dam")

    if "Monomonie" in line:
        line = line.replace("Monomonie", "Menomonie")

    if "Cookville" in line:
        line = line.replace("Cookville", "Cookeville")

    if "New Port Richley" in line:
        line = line.replace("New Port Richley", "New Port Richey")

    if "Pentiction" in line or "Pentcton" in line:
        line = line.replace("Pentiction", "Penticton")
        line = line.replace("Pentcton", "Penticton")

    if "…" in line:
        line = line.replace("…", "")

    if "Renfew" in line:
        line = line.replace("Renfew", "Renfrew")

    if "Surray" in line:
        line = line.replace("Surray", "Surrey")

    if "Mcmurray" in line:
        line = line.replace("Mcmurray", "McMurray")
    
    if "Mccleary" in line:
        line = line.replace("Mccleary", "McCleary")

    if "S.Africa Workers List" in line:
        line = line.replace("S.Africa Workers List", "South Africa Workers List")

    # Replace SK with Saskatchewan using regex
    line = re.sub(r'\bSK\b', 'Saskatchewan', line)

    # Handle Winter/Spring pattern with asterisks
    if "*Winter/Spring" in line and "*Winter/Spring*" not in line:
        line = line.replace("*Winter/Spring", "*Winter/Spring*")

    if "Manitoba and Northwest Ontario" in line:
        line = line.replace("Manitoba and Northwest Ontario", "Manitoba/Northwest Ontario")

    if "Argentina/Paraguay/Uruguay, Rio Grande Do Sul" in line:
        line = line.replace("Argentina/Paraguay/Uruguay, Rio Grande Do Sul", "Argentina/Paraguay/Uruguay/Brazil Rio Grande do Sul")

    # Special case for Canada Workers List followed by a province
    if line.startswith("Canada Workers List"):
        for province in countries['Canada']['states']:
            if province in line:
                line = line.replace("Canada Workers List", f"{province} Canada Workers List")
                break

    result = {
        'type': 'Workers List',
        'country': None,
        'state': None,
        'location': None,
        'note': 'Workers List',
        'month': None,
        'start_date': None,
        'end_date': None
    }
    
    # Find the position of "Workers List" and split the line
    workers_list_pos = line.lower().find('workers list')
    if workers_list_pos >= 0:
        text_before = line[:workers_list_pos].strip()
        text_after = line[workers_list_pos + len('workers list'):].strip()
    else:
        workers_list_pos = line.lower().find('staff')
        if workers_list_pos >= 0:
            text_before = line[:workers_list_pos].strip()
            text_after = line[workers_list_pos + len('staff'):].strip()
    print_debug(f"\n\nBOB WL 1.0 - text_before: {text_before}")
    print_debug(f"BOB WL 1.1 - text_after: {text_after}")
    # Remove month names and their variations first

    month_or_range = get_month_or_range(text_before)
    if month_or_range:
        print_debug(f"BOB WL 1.2 - month_match: {month_or_range}")
        text_before = text_before.replace(month_or_range, '')
        result['note'] = add_to_note_list(result['note'], f"{month_or_range} List")
        result['month'] = month_or_range

    print_debug(f"BOB WL 2.0 - text_before: {text_before}")
    print_debug(f"BOB WL 2.1 - result['note']: {result['note']}")
    print_debug(f"BOB WL 2.2 - text_after: {text_after}")

    # remove any spaces or commas from the beginning of the text_before
    text_after = re.sub(r'^[\s,]+', '', text_after)
    

    print_debug(f"BOB WL 2.21 - text_after: {text_after}")

    the_location = None
    note_from_parens = ''
    # Look for text in parentheses in the text after Workers List
    # Look for text in parentheses in the text after Workers List
    paren_match = re.search(r'\((.*?)\)', text_after)
    if paren_match:
        # From text_after, remove the paren_matching text
        straggler = re.sub(r'\(.*?\)', '', text_after).strip()
        print_debug(f"BOB WL 2.211 - straggler: {straggler}")

        paren_text = paren_match.group(1).strip()

        if 'Interlake MB' in paren_text:
            paren_text = paren_text.replace('Interlake MB', 'Interlake')

        special_case_phrase, paren_text = handle_paren_text_patterns(paren_text)
        the_location, note_from_parens, straggler = format_paren_text_note(special_case_phrase, paren_text, straggler)
        if the_location:
            the_location = the_location.replace("/", ", ")  # in the location, substitue / with , space as that is how they are done consistently in countries
            print_debug(f"BOB WL 2.2111 - the_location: {the_location}")
            loc_result = get_state_country(the_location, countries)
            print_debug(f"\nBOB WL 2.212 - country: {loc_result['country']} state: {loc_result['state']} location: {loc_result['location']}")
            if loc_result['location'] and loc_result['line'] == '':
                print_debug(f"BOB WL 2.2121 - loc_result['location']: {loc_result['location']}  |  result['location']: {result['location']}")
                print_debug(f"BOB WL 2.2122 - loc_result['state']: {loc_result['state']}  |  result['state']: {result['state']}")
                print_debug(f"BOB WL 2.2123 - loc_result['country']: {loc_result['country']}  |  result['country']: {result['country']}")
                print_debug(f"BOB WL 2.2124 - loc_result['line']: {loc_result['line']}")
                result['location'] = loc_result['location']
                if loc_result['state'] and not result['state']:
                    result['state'] = loc_result['state']
                if loc_result['country'] and not result['country']:
                    result['country'] = loc_result['country']
            else:
                text_after = paren_text.replace(the_location, '')
                text_after += (', ' + straggler) if straggler and '*' not in straggler else (' ' + straggler) if straggler else ''
        else:
            result['location'] = the_location

        if note_from_parens:
            result['note'] = add_to_note_list(result['note'], note_from_parens)

        # Remove () if that's all that remains in text_after
        text_after = re.sub(r'\(.*?\)', '', text_after).strip()
        print_debug(f"BOB WL 2.213 - special_case_phrase: {special_case_phrase}   | paren_text: {paren_text}")
        print_debug(f"BOB WL 2.214 - the_location: {the_location}   | note_from_parens: {note_from_parens}   | straggler: {straggler}")
        print_debug(f"BOB WL 2.215 - country: {result['country']}   | state: {result['state']}   | location: {result['location']}  | note: {result['note']}")
        print_debug(f"BOB WL 2.216 - text_after after removing parentheses: {text_after}")
        #text_after += (' - ' + straggler) if straggler else ''


    print_debug(f"BOB WL 3.0 - text_after: {text_after}")
    print_debug(f"BOB WL 3.1 - result['note']: {result['note']}")

    # Look for CCCC text before any asterisked text
    # First find where any asterisked text starts
    asterisk_pos = text_after.find('*')
    if asterisk_pos == -1:
        asterisk_pos = len(text_after)
    
    # Get the text before any asterisks
    text_before_asterisks = text_after[:asterisk_pos].strip()

    print_debug(f"BOB WL 3.11 - text_before_asterisks: {text_before_asterisks}")
    
    # Look for "with" patterns at the start
    with_match = re.match(r'(.*?)(?:with|With|w/|w/\s+)(.+)$', text_before_asterisks)
    if with_match:
        # If it starts with a "with" pattern, add "With " + the rest

        print_debug(f"BOB WL 3.111 - with_match groups count: {len(with_match.groups())}")
        before, after = with_match.groups()
        before_stripped = before.strip()
        if before_stripped.startswith(','):
            before_stripped = before_stripped[1:].strip()
        print_debug(f"BOB WL 3.112 - before_stripped: |{before_stripped}|")
        cccc_text = f"{before_stripped}{',' if before_stripped and not before_stripped.endswith(',') else ''}With {' '.join(after.split())}"
        print_debug(f"BOB WL 3.12 - cccc_text: {cccc_text}")
    else:
        # If no "with" pattern, use the whole text
        if text_before_asterisks.startswith(','):
            text_before_asterisks = text_before_asterisks[1:].strip()
        cccc_text = text_before_asterisks
        print_debug(f"BOB WL 3.13 - cccc_text: {cccc_text}")
    
    # If we found CCCC text, add it to the note
    if cccc_text:
        # Append to existing note
        result['note'] = add_to_note_list(result['note'], cccc_text)
        print_debug(f"BOB WL 3.14 - result['note']: {result['note']}  |  asterisk_pos: {asterisk_pos}")
        # Check to see if there's a month range in cccc_text
        month_or_range = get_month_or_range(cccc_text)
        if month_or_range:
            result['month'] = month_or_range

        # Remove the CCCC text from the line
        text_after = text_after[asterisk_pos:].strip()
        print_debug(f"BOB WL 3.15 - text_after: {text_after}")

    print_debug(f"BOB WL 4.0 - text_after: {text_after}")
    print_debug(f"BOB WL 4.1 - result['note']: {result['note']}")

    # Look for text between asterisks
    asterisk_match = re.search(r'\*(.*?)\*', text_after)
    if asterisk_match:
        asterisk_text = asterisk_match.group(1).strip()
        # Append to existing note
        result['note'] = add_to_note_list(result['note'], asterisk_text)
        month_or_range = get_month_or_range(asterisk_text)
        if month_or_range:
            if '/' in asterisk_text:
                asterisk_text = asterisk_text.replace('/', '-')
                month_or_range = get_month_or_range(asterisk_text)
                if month_or_range:
                    result['month'] = month_or_range
            else:
                result['month'] = month_or_range

        # Remove the asterisks and their contents from the line
        text_after = re.sub(r'\*.*?\*', '', text_after).strip()

    print_debug(f"BOB WL 5.0 - text_after: {text_after}")
    print_debug(f"BOB WL 5.1 - result['note']: {result['note']}")

    # Look for w/ patterns in text after asterisks
    w_with_match = re.search(r'(?:with|With|\bw\/)(?:\s*)([^\s](?:.+?)(?:\s|$))', text_after)
    if w_with_match:
        w_with_text = w_with_match.group(1).strip()
        # Append to existing note
        result['note'] = add_to_note_list(result['note'], f"With {w_with_text}")
        # Remove the matched text from the line
        text_after = re.sub(r'\bw\/([A-Za-z]+ [A-Za-z]+)', '', text_after).strip()

    print_debug(f"BOB WL 6.0 - text_after: {text_after}")
    print_debug(f"BOB WL 6.1 - result['note']: {result['note']}")

    if text_after:
        # Look for date ranges like Jan-Jun
        month_or_range = get_month_or_range(text_after)
        if month_or_range:
            # Append to existing note
            result['note'] = add_to_note_list(result['note'], month_or_range)
            result['month'] = month_or_range
            # Remove the date range from the text
            text_after = text_after.replace(month_or_range, '')

    print_debug(f"BOB WL 7.0 - text_after: {text_after}")
    print_debug(f"BOB WL 7.1 - result['note']: {result['note']}")

    # Check if the text before Workers List is a country or state/province
    found_country = None
    found_state = None
    remaining_text = text_before

    print_debug(f"BOB WL 8.0 - text_before: {text_before}")
    state_country_info = get_state_country(text_before, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    if state_country_info['location']:
        result['location'] = state_country_info['location']

    if not the_location and cccc_text:
        the_location = cccc_text
        
    if not result['location'] and the_location:
        print_debug(f"\nBOB WL 8.01 - text_before: {text_before + ' | ' + the_location}")
        state_country_info = get_state_country(text_before + ' ' + the_location, countries)
        print_debug(f"BOB WL 8.001 - country: {state_country_info['country']}")
        print_debug(f"BOB WL 8.002 - state: {state_country_info['state']}")
        print_debug(f"BOB WL 8.003 - location: {state_country_info['location']}")
        print_debug(f"BOB WL 8.004 - line: {state_country_info['line']}")
        if state_country_info['state']:
            result['state'] = state_country_info['state']
        if state_country_info['location']:
            result['location'] = state_country_info['location']
        else:
            # check to see if the_location is a location in a country in state_country_info['country'] and in state_country_info['states'] of that same country
            for country_name, country in countries.items():
                if country_name == state_country_info['country'] and 'cities' in country:
#BOB3
                    print_debug(f"BOB WL 8.000001 - the_location: {the_location} in country['cities'].  {country_name}")
                    # Normalize the apostrophe in the_location
                    if the_location in country['cities']:
                        states = country['cities'][the_location]
                        print_debug(f"BOB WL 8.000002 - states: {states}")
                        # for city_name, city_value in country['cities'].items():
                        #     print_debug(f"BOB WL 8.0000021 - City: {city_name} : {city_value[0]}")
                        print_debug(f"BOB WL 8.000002 - Yep it's in there")
                        # Print all cities and their values
                        if result['state'] and result['state'] in states:
                            print_debug(f"BOB WL 8.000003 - the_location: {the_location} in country['cities'].  {country_name}")
                            result['location'] = the_location
                            break

    result = adjust_location_result(result)

    text_before = state_country_info['line']

    print_debug(f"BOB WL 8.1 - result['country']: {result['country']}")
    print_debug(f"BOB WL 8.2 - result['state']: {result['state']}")
    print_debug(f"BOB WL 8.3 - result['location']: {result['location']}")
    print_debug(f"BOB WL 8.4 - result['note']: {result['note']}")

    return result

def handle_travel(line: str, countries: Dict) -> Optional[Dict]:
    """Handle travel-related entries."""
    result = {
        'type': 'Travel',
        'country': None,
        'state': None,
        'location': None,
        'note': None
    }

    # Pattern for visiting or returning to a location
    travel_patterns = [
        (r'^(?:Visiting|Visit\s+to)\s+([A-Za-z\s]+)$', 'Visiting'),
        (r'^(?:Return|Returned)\s+to\s+([A-Za-z\s]+)$', 'Return to'),
        (r'^Home\s+Visit\s+to\s+([A-Za-z\s]+)$', 'Home Visit'),
        (r'^Return\s+to\s+([A-Za-z\s]+)\s+\(([^)]+)\)$', 'Return to'),  # For "Return to E. Canada" pattern
        (r'^([A-Za-z\s]+)\s+([A-Za-z\s]+)\s+\(Home\s+Visit\)$', 'Home Visit')  # For "Victoria Australia (Home Visit)" pattern
    ]

    for pattern, travel_type in travel_patterns:
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            
            state_country_info = get_state_country(line, countries)
            if state_country_info['country']:
                result['country'] = state_country_info['country']
            if state_country_info['state']:
                result['state'] = state_country_info['state']
            if state_country_info['location']:
                result['location'] = state_country_info['location']
            elif state_country_info['state']:
                result['location'] = state_country_info['state']


            result = adjust_location_result(result)

            result['note'] = f"{travel_type} {result['country']}"
            return result

    return None

def handle_started_work(line: str, countries: Dict) -> Optional[Dict]:
    """Handle patterns indicating when someone started in the work."""
    # Only process lines that contain "Started in the work"
    if 'Started in the work' not in line:
        return None

    result = {
        'type': 'Started Work',
        'country': '',
        'state': '',
        'location': '',
        'note': 'Started in the work',
        'month': None,
        'start_date': None,
        'end_date': None
    }

    # Remove the "Started in the work" text and any surrounding characters
    line = re.sub(r'(?:\*+|\(|\s*,)?\s*Started\s+in\s+the\s+work\s*(?:\*+|\))?', '', line, flags=re.IGNORECASE).strip()

    # Check for date pattern (e.g., "July 6")
    date_match = re.match(r'^(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*\d*', line, flags=re.IGNORECASE)
    if date_match:
        result['month'] = date_match.group(1)
        for i in range(date_match.lastindex + 1):  # Iterate through all captured groups
            print_debug(f"BOB SW 0.1 - Group {i}: {date_match.group(i)}  |  date_match.groups(): {date_match.groups()}")
        date_pieces = date_match.group(0).split()
        if len(date_pieces) >= 1:
            month = MONTH_MAP.get(date_pieces[0], date_pieces[0])
            if len(date_pieces) >= 2:
                day_pieces = date_pieces[1].split('-')
                # Get start and possible end date
                if len(day_pieces) >= 1:
                    day = day_pieces[0].zfill(2)  # Pad day with leading zero if needed
                    result['start_date'] = f"{month}/{day}"
                    if len(day_pieces) >= 2:
                        end_day = day_pieces[1].zfill(2)  # Pad day with leading zero if needed
                        result['end_date'] = f"{month}/{end_day}"
        print_debug(f"BOB SW 0.2 - result['start_date']: {result['start_date']}  |  result['end_date']: {result['end_date']}")

        #result['start_date'] = len(date_match.groups())
        line = line[date_match.end():].strip()

    state_country_info = get_state_country(line, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    if state_country_info['location']:
        result['location'] = state_country_info['location']
    if state_country_info['line']:
        result['note'] = result['note'] + ': ' + state_country_info['line']

    result = adjust_location_result(result)

    return result

def get_photo_type(line: str) -> Tuple[str, str]:
    """Get the photo type from the line and return both the type and the remaining line.
    Returns a tuple of (photo_type, remaining_line)"""
    # Check for specific photo types in order
    photo_types = [
        ('Worker Staff Photo', 'Worker Staff Photo'),
        ('Workers Meeting Photo', 'Workers Meeting Photo'),
        ('Staff Photo', 'Staff Photo'),
        ('Workers Photo', 'Workers Photo'),
        ('Special Meeting Photo', 'Special Meeting Photo'),
        ('Photo', 'Photo'),
        ('Workers Picture', 'Workers Picture')
    ]

    for photo_type, info_value in photo_types:
        if photo_type.lower() in line.lower():
            remaining_line = re.sub(photo_type, '', line, flags=re.IGNORECASE).strip()
            return info_value, remaining_line
    
    return None, line

def handle_photo(line: str, countries: Dict) -> Optional[Dict]:
    """Handle photo patterns by ignoring them."""

    if 'photo' not in line.lower() and 'picture' not in line.lower():
        return None

    # Return None if 'absent' is found in the line
    if 'absent' in line.lower():
        return None

    result = {
        'type': 'Photo',
        'country': None,
        'state': None,
        'location': None,
        'note': None,
        'start_date': None,
        'end_date': None
    }

    # Get state and country information
    state_country_info = get_state_country(line, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    result['location'] = state_country_info['location']

    result = adjust_location_result(result)
        
    line = state_country_info['line']

    print_debug(f"\n\nBOB PHOTO country: {result['country']}")
    print_debug(f"BOB state: {result['state']}")
    print_debug(f"BOB location: {result['location']}")
    print_debug(f"BOB line: {line}")

    # Get photo type and remaining line
    photo_type, line = get_photo_type(line)
    if photo_type:
        result['note'] = photo_type

    return result

def handle_workers_meeting(line: str, countries: Dict) -> Optional[Dict]:
    """Handle workers meeting patterns."""

    if 'workers meeting' not in line.lower():
        return None

    result = {
        'type': 'Workers Meeting',
        'country': None,
        'state': None,
        'location': None,
        'note': None,
    }

    # Remove the "workers meeting" text and any surrounding characters
    line = re.sub(r'[*\(]?\s*Workers\s+Meeting\s*[*\)]?', ' ', line, flags=re.IGNORECASE).strip()

    # Check for (state) in the line.  Can be (Colorado) or (MO) format.  Grab into location and replace string in line
    # If state is a 2 character code, look it up in coutries using state_abbreviations and use the states full name
    visiting_from = None
    state_match = re.search(r'\(([^)]+)\)', line)
    if state_match:
        state = state_match.group(1)
        if len(state) == 2:
            # Look up state abbreviation in state_variations for both US and Canada
            for country, info in countries.items():
                if 'state_variations' in info and state in info['state_variations']:
                    visiting_from = info['state_variations'][state]
                    break
        else:
            visiting_from = state
        line = re.sub(r'\(([^)]+)\)', '', line)

    # Get state and country information
    state_country_info = get_state_country(line, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    if state_country_info['location']:
        result['location'] = state_country_info['location']

    line = state_country_info['line']

    result['note'] = line + (' Workers Meeting' if line else 'Workers Meeting')
    
    if visiting_from:
        result['note'] = result['note'] + ' Visiting from ' + visiting_from

    result = adjust_location_result(result)

    return result
    
def handle_removed_from(line: str, countries: Dict) -> Optional[Dict]:
    """Handle Removed from work patterns."""
    if 'removed from' not in line.lower():
        return None

    result = {
        'type': 'Removed',
        'country': None,
        'state': None,
        'location': None,
        'note': None,
        'month': None
    }

    # Find the text starting with "removed from" and store it in note
    removed_match = re.search(r'removed from.*$', line, re.IGNORECASE)
    if removed_match:
        result['note'] = removed_match.group(0).strip()
        # Remove the matched text from the line
        line = line[:removed_match.start()].strip()

    # Get state and country information from the remaining line
    state_country_info = get_state_country(line, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']

    result = adjust_location_result(result)

    line = state_country_info['line']

    # Check for month abbreviation in remaining text
    if line:
        # Look for month abbreviation at the start of the remaining text
        month_match = re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', line, re.IGNORECASE)
        if month_match:
            result['month'] = month_match.group(1)

    return result

def handle_guestbook(line: str, countries: Dict) -> Optional[Dict]:
    """Handle guestbook patterns."""
    
    if 'guestbook' not in line.lower() and 'guest book' not in line.lower():
        return None
    
    result = {
        'type': 'Guestbook',
        'location': None,
        'note': 'Guestbook',
        'state': None,
        'country': None,
        'month': None
    }
    
    # Remove specific guestbook patterns
    line = re.sub(r'\(guestbook\)|\(member guestbook\)|\(guest book entry\)', '', line, flags=re.IGNORECASE).strip()

    state_country_info = get_state_country(line, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    line = state_country_info['line']

    # Look for fully spelled out month at the start of the line
    month_match = re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December)', line, re.IGNORECASE)
    if month_match:
        result['month'] = month_match.group(1)
        # Remove the month from the line and store the rest in note
        line = line[month_match.end():].strip()
    
    if line:
        result['note'] = result['note'] + ': ' + line

    result = adjust_location_result(result)

    return result
   
def handle_location_only(line: str, countries: Dict) -> Optional[Dict]:
    """Handle location only patterns."""

    result = {
        'type': 'Location',
        'country': None,
        'state': None,
        'location': None,
        'note': None,
        'month': None,
        'start_date': None,
        'end_date': None
    }

    print_debug(f"\n\nBOB LOC 1.0 - line: {line}")

    state_country_info = get_state_country(line, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    if state_country_info['location']:
        result['location'] = state_country_info['location']
    line = state_country_info['line']

    print_debug(f"BOB LOC 1.01 - country: {result['country']}  |  state: {result['state']}  |  location: {result['location']}  |  line: {line}")

    protem_case = ''

    if line:
        paren_match = re.search(r'\((.*?)\)', line)
        if paren_match:
            paren_text = paren_match.group(1).strip()

            parts = re.split(r'\s*/\s*', paren_text)
            # Join with comma and space
            paren_text_fixed = ', '.join(parts)

#BOB2
            print_debug(f"BOB LOC 1.1 - paren_text_fixed: {paren_text_fixed}")
            print_debug(f"BOB LOC 1.101- location: {result['location']}")
            if paren_text_fixed and (result['location'] == None or result['location'] == ''):
                print_debug(f"BOB LOC 1.10 - potential_city: |{paren_text_fixed}|")
                # First check if the full paren_text_fixed string exists in the cities dictionary
                for country_name, country in countries.items():
                    if country_name == result['country'] and 'cities' in country:
                        if paren_text_fixed in country['cities']:
                            print_debug(f"BOB LOC 1.101 - {paren_text_fixed} in country['cities'] - {country['cities'][paren_text_fixed]}  state: {result['state']}")
                            if result['state'] and result['state'] in country['cities'][paren_text_fixed]:
                                print_debug(f"BOB LOC 1.102 - {paren_text_fixed} in country['cities'] and result['state'] matches")
                                result['location'] = paren_text_fixed
                                line = line.replace(paren_text, '')
                                line = re.sub(r'\(.*?\)', '', line).strip()
                                paren_text = ''
                                paren_text_fixed = ''
                                break

            the_note = ''
            special_case = ''
            absent_case = ''
            if paren_text_fixed:
                print_debug(f"BOB LOC 1.11 - paren_text_fixed: {paren_text_fixed}")
                
                if paren_text_fixed.lower().startswith('Return To '):
                    special_case = "return to"
                    the_note = 'Return To ' + paren_text_fixed[10:].strip()
                if paren_text_fixed.lower().startswith('to '):
                    special_case = "to"
                    the_note = 'To ' + paren_text_fixed[3:].strip()
                if paren_text_fixed.lower().endswith('pro tem'):
                    protem_case = "pro tem"
                if 'Absent' in paren_text_fixed:
                    absent_case = "absent"
                    the_note = 'Absent'
                if special_case or protem_case or absent_case:
                    result['note'] = the_note
                else:
                    print_debug(f"BOB LOC 1.12 - paren_text_fixed: {paren_text_fixed}")
                    print_debug(f"BOB LOC 1.12 - result['note']: {result['note']}")
                    month_pattern = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b'
                    month_match = re.search(month_pattern, paren_text_fixed, re.IGNORECASE)
                    if month_match:
                        result['note'] = 'Visiting in ' + paren_text_fixed
                    else:
                        result['note'] = 'Visiting from ' + paren_text_fixed
                    print_debug(f"BOB LOC 1.13 - result['note']: {result['note']}")
                # Remove the paren_text from the line as it is determined to be a location
                line = line.replace(paren_text, '')
                # Strip out the () from the line
                line = re.sub(r'\(.*?\)', '', line).strip()
                paren_text = ''
                paren_text_fixed = ''

    if line:
        # Check for date pattern (e.g., "March 8")
        date_match = re.match(r'^(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*\d*', line, flags=re.IGNORECASE)
        if date_match:
            result['month'] = date_match.group(1)
            for i in range(date_match.lastindex + 1):  # Iterate through all captured groups
                print_debug(f"BOB LOC DATE 1.0 - Group {i}: {date_match.group(i)}  |  date_match.groups(): {date_match.groups()}")
            date_pieces = date_match.group(0).split()
            if len(date_pieces) >= 1:
                month = MONTH_MAP.get(date_pieces[0], date_pieces[0])
                if len(date_pieces) >= 2:
                    day_pieces = date_pieces[1].split('-')
                    # Get start and possible end date
                    if len(day_pieces) >= 1:
                        day = day_pieces[0].zfill(2)  # Pad day with leading zero if needed
                        result['start_date'] = f"{month}/{day}"
                        if len(day_pieces) >= 2:
                            end_day = day_pieces[1].zfill(2)  # Pad day with leading zero if needed
                            result['end_date'] = f"{month}/{end_day}"
            print_debug(f"BOB LOC DATE 2.0 - result['start_date']: {result['start_date']}  |  result['end_date']: {result['end_date']}")


    print_debug(f"BOB LOC 1.2 - line: {line}")
    # Replace any occurrence of w/ or lowercase with with With
    if line:
        line = re.sub(r'\b(with|w/)\b(\s*)(?=[A-Z])', 'With ', line)
        result['note'] = add_to_note_list(result['note'] if result['note'] else '', line)
        if protem_case:
            result['note'] = add_to_note_list(result['note'], 'pro tem')

    result = adjust_location_result(result)

    print_debug(f"BOB LOC 1.3 - line: {line}")
    print_debug(f"BOB LOC 2.0 - country: {result['country']}")
    print_debug(f"BOB LOC 2.1 - state: {result['state']}")
    print_debug(f"BOB LOC 2.2 - location: {result['location']}")
    print_debug(f"BOB LOC 2.3 - note: {result['note']}")
    
    if result['country'] or result['state'] or result['location'] or result['note']:
        return result
    
    return None

def process_text_patterns(line: str, original_text: str) -> Dict:
    """Process text patterns and extract relevant information."""
    result = {
        'type': None,
        'country': None,
        'state': None,
        'location': None,
        'note': None,
        'original_text': original_text,
        'fixed': line,
        'start_date': None,
        'end_date': None,
    }

    # Clean up the line by removing "Visited" and "for"
    #line = re.sub(r'^Visited\s+', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s+for\s+', ' ', line, flags=re.IGNORECASE)
    # Remove trailing commas after Meeting or Convention
    line = re.sub(r'((?:Meeting|Convention))\s*,\s*$', r'\1', line, flags=re.IGNORECASE)

    result['fixed'] = line

    # Try each handler in sequence
    handlers = [
        handle_workers_list,
        handle_convention,
        handle_special_meeting,
        handle_travel,
        handle_started_work,
        handle_photo,
        handle_workers_meeting,
        handle_removed_from,
        handle_guestbook,
        handle_location_only
    ]

    for handler in handlers:
        handler_result = handler(line, countries)
        if handler_result:
            result.update(handler_result)
            return result

    return result

def text_fixes(line: str) -> str:
    """Apply text fixes to the line."""
    if '(Escondido/Ramona' in line:
        if '(Escondido/Ramona)' not in line:
            line = line.replace('(Escondido/Ramona', '(Escondido/Ramona)')

    if 'Convvention' in line:
        line = line.replace('Convvention', 'Convention')
    
    if 'Sart-Dames- Avelines' in line:
        line = line.replace('Sart-Dames- Avelines', 'Sart-Dames-Avelines')
    
    if 'Ducan Canada' in line:
        line = line.replace('Ducan Canada', 'Duncan Canada')

    if 'Greenshields' in line:
        line = line.replace('Greenshields', 'Greenshield')

    if 'Iron Bridges' in line:
        line = line.replace('Iron Bridges', 'Iron Bridge')

    if 'Seagraves' in line:
        line = line.replace('Seagraves', 'Seagrave')

    if 'Watt NSW Australia' in line:
        line = line.replace('Watt NSW Australia', 'Watta NSW Australia')

    if 'NSW' in line:
        line = line.replace('NSW', 'New South Wales')

    if 'Insurgents Mexico Convention' in line:
        line = line.replace('Insurgents', 'Insurgentes')

    if 'Insurgentes Baja' in line:
        line = line.replace('Insurgentes Baja', 'Insurgentes')

    if 'Almonte New York' in line:
        line = line.replace('Almonte', 'Altamont')

    if 'Dagar Montana' in line:
        line = line.replace('Dagar', 'Dagmar')

    if 'Miltown 2 Washington' in line:
        line = line.replace('Miltown', 'Milltown')

    if 'MIlltown 1 Washington' in line:
        line = line.replace('MIlltown', 'Milltown')

    if 'Mountain 1 Ranch' in line:
        line = line.replace('Mountain 1 Ranch', 'Mountain Ranch 1')

    if 'Mountain 2 Ranch' in line:
        line = line.replace('Mountain 2 Ranch', 'Mountain Ranch 2')

    if 'Perris Tennessee' in line:
        line = line.replace('Perris', 'Paris')

    if 'Roger Arkansas' in line:
        line = line.replace('Roger', 'Rogers')

    if 'Yellow Spring Ohio' in line:
        line = line.replace('Yellow Spring', 'Yellow Springs')

    if 'Post Falls,' in line:
        line = line.replace('Post Falls,', 'Post Falls')

    if 'Madisonville,' in line:
        line = line.replace('Madisonville,', 'Madisonville')

    if 'Dells,' in line:
        line = line.replace('Dells,', 'Dells')

    if 'Chaintreauville,' in line:
        line = line.replace('Chaintreauville,', 'Chaintreauville')

    if 'Ales,' in line:
        line = line.replace('Ales,', 'Ales')

    if 'Bonao,' in line:
        line = line.replace('Bonao,', 'Bonao')

    if 'Sart-Dames-Avelines,' in line:
        line = line.replace('Sart-Dames-Avelines,', 'Sart-Dames-Avelines')

    if 'Yorkton/Fort' in line:
        line = line.replace('Yorkton/Fort', 'Yorkton, Fort')

    if 'Brazil and Uruguay' in line:
        line = line.replace('Brazil and Uruguay', 'Brazil/Uruguay')
       
    if "’" in line:
        # DO NOT MODIFY OR REMOVE THIS LINE - Critical for handling apostrophes
        # This line specifically handles the conversion of curly apostrophes to straight apostrophes
        # Any modification to this line could break text 
        # Trying what_to_replace = "’" to see if I can get the AI to stop trying to change the line
        what_to_replace = "’"
        line = line.replace(what_to_replace, "'")
        

    # Fix Glen Valley variations
    line = re.sub(r'[Gg][Ll][Ee][Nn]\s*[Vv][Aa][Ll][Ll][Ee][Yy]\s*(\d+)', r'Glen Valley \1', line, flags=re.IGNORECASE)

    return line

def process_file(filepath: str, validate_mode: bool = False, header_output: bool = False) -> None:
    """Process a single file and update the database or just look at patterns."""
    global perp_name
    filename = os.path.basename(filepath)
    perp_name = extract_perp_name(filename)
    
    if not perp_name:
        print(f"Could not extract perp name from {filename}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

                   
            # Handle multi-line entries with split parentheses
            if '(' in line and ')' not in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not re.match(r'^\d{4}', next_line):
                    line = f"{line} {next_line}"
                    i += 1  # Skip the next line since we've combined it

            year_info = parse_year_line(line)
            if year_info:
                start_year, end_year = year_info
                end_year = end_year or start_year
                year_str = str(start_year) if end_year == start_year else f"{start_year}-{end_year}"
                
                try:
                    # Process the text after the year
                    text_after_year = line[line.find(str(start_year)) + len(str(start_year)):].strip()
                    if end_year and end_year != start_year:
                        text_after_year = text_after_year[text_after_year.find(str(end_year)) + len(str(end_year)):].strip()
                    # Remove any duplicate year at the start of text_after_year
                    text_after_year = re.sub(r'^\d{4}\s*', '', text_after_year)
                    # Remove any duplicate year that appears after a hyphen
                    text_after_year = re.sub(r'-\s*\d{4}\s*', '', text_after_year)

                    original_text = text_after_year
                    text_after_year = text_fixes(text_after_year)

                    pattern_result = process_text_patterns(text_after_year, original_text)
                    if pattern_result['type']:
                        # Output header if not already done
                        if not header_output:
                            header_parts = [
                                'Status',
                                'Perp Name',
                                'Year',
                                'Type',
                                'Country',
                                'State',
                                'Location',
                                'Note',
                                'Start Date',
                                'End Date',
                                'Month',
                                'Original Text',
                                'Fixed Text'
                            ]
                            print('|'.join(header_parts))
                            header_output = True

                        # Format: MATCHED YYYY \t TTTT \t LLLL \t SSSS \t CCC \t NNNN
                        note = pattern_result.get('note', '')
                        date_info = pattern_result.get('date_info', '')
                        if date_info:
                            note = f"{note} **{date_info}"
                        output_parts = [
                            'MATCHED',
                            perp_name,
                            year_str,
                            pattern_result['type'],
                            pattern_result.get('country') or '',
                            pattern_result.get('state') or '',
                            pattern_result.get('location') or '',
                            pattern_result.get('note') or '',
                            pattern_result.get('start_date') or '',
                            pattern_result.get('end_date') or '',
                            pattern_result.get('month') or '',
                            pattern_result.get('original_text') or '',
                            pattern_result.get('fixed') or ''
                        ]
                        separator = '|'
                        print(separator.join(output_parts))
                    else:
                        # For non-matching lines, output with NOMATCH prefix only in validate mode
                        #if validate_mode:
                        print(f"NOMATCH - {line}")
                except Exception as e:
                    print(f"Error processing line: {line}")
                    print(f"Error details: {str(e)}")
            i += 1

def main():
    """Main function to process input files."""
    global validate_mode
    parser = argparse.ArgumentParser(description='Process location files and update database')
    parser.add_argument('--file', type=str, help='Process a single file by name')
    parser.add_argument('--validate', action='store_true', help='Validate mode - process patterns without database interaction')
    parser.add_argument('--input-dir', type=str, default='inputs', help='Directory containing input files (default: inputs)')
    args = parser.parse_args()

    # Set global validate mode
    validate_mode = args.validate

    input_dir = args.input_dir
    
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' not found")
        return

    # Track if we've output the header
    header_output = False

    if args.file:
        # Process single file
        filepath = os.path.join(input_dir, args.file)
        if not os.path.exists(filepath):
            print(f"File '{args.file}' not found in {input_dir}")
            return
        if not args.file.endswith(('_from_pdf.txt', '_from_txt.txt')):
            print(f"File '{args.file}' does not match required pattern (_from_pdf.txt or _from_txt.txt)")
            return
        
        if args.validate:
            print(f"Processing single file: {args.file}")
        
        process_file(filepath, args.validate, header_output)
    else:
        # Process all matching files
        for filename in os.listdir(input_dir):
            if filename.endswith(('_from_pdf.txt', '_from_txt.txt')):
                if filename.lower().startswith('cases ') or 'OLDER' in filename:
                    if args.validate:
                        print(f"Skipping cases or OLDER file: {filename}")
                    continue
                filepath = os.path.join(input_dir, filename)
                if args.validate:
                    print(f"Processing {filename}...")
                process_file(filepath, args.validate, header_output)
                header_output = True  # Set to True after first file is processed

if __name__ == '__main__':
    main()