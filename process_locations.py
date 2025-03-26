import os
import re
import argparse
from datetime import datetime
import sys
import time
from dotenv import load_dotenv
from typing import Optional, Tuple, Dict, List
from countries_data import countries

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
    # Replace multiple spaces with a single space and strip
    text = re.sub(r'\s+', ' ', text).strip()
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

    print(f"\n\nBOB STATE COUNTRY 0.0 - Line: {line}")
    line = re.sub(r'\bN\.?\s+', 'North ', line)
    line = re.sub(r'\bS\.?\s+', 'South ', line)
    line = re.sub(r'\bW\.?\s+', 'West ', line)
    line = re.sub(r'\bNW\.?\s+', 'Northwest ', line)
    line = re.sub(r'\bNE\.?\s+', 'Northeast ', line)
    line = re.sub(r'\bSW\.?\s+', 'Southwest ', line)
    line = re.sub(r'\bSE\.?\s+', 'Southeast ', line)

    # First check if any word in the line is a city
    words = line.split()
    for i in range(len(words)):
        # Try 3, 2, or 1 consecutive words (in that order)
        for word_count in range(3, 0, -1):
            if i + word_count <= len(words):
                potential_city = ' '.join(words[i:i + word_count])
                for country, info in countries.items():
                    if 'cities' in info and potential_city in info['cities']:  # Remove check for info['cities'][potential_city]
                        # Found a city, get its state (may be None)
                        state = info['cities'][potential_city]
                        result['state'] = state
                        result['country'] = country
                        # Remove the state and country from the line
                        if state:  # Only remove state if it exists
                            line = line.replace(state, '').strip()
                        line = line.replace(country, '').strip()
                        line = line.replace(potential_city, '').strip()
                        # Remove any state variations
                        if 'state_variations' in info:
                            for variation in info['state_variations'].keys():
                                line = line.replace(variation, '').strip()
                        # Set location to city name
                        print(f"BOB - Location: {potential_city}")
                        result['location'] = potential_city
                        # Keep the remaining text in the line field
                        print(f"BOB - Line: {line}")
                        result['line'] = line
                        return result
    print(f"\n\nBOB 1.0 - Line: {line}")
    # First check for combined country names
    for country, info in countries.items():
        if '/' in country and country in line:
            result['country'] = country
            # Check for states in this country
            for state in info.get('states', []):
                if state and state in line:  # Skip empty strings
                    result['state'] = state
                    # Remove the state and country from the line
                    line = line.replace(state, '').strip()
                    line = line.replace(country, '').strip()
                    result['line'] = clean_line(line)
                    # DAW result['location'] = clean_line(line)
                    return result
            # If no state found in this country, check for states in other countries
            for other_country, other_info in countries.items():
                if other_country != country:
                    for state in other_info.get('states', []):
                        if state and state in line:  # Skip empty strings
                            result['state'] = state
                            # Remove the state and country from the line
                            line = line.replace(state, '').strip()
                            line = line.replace(country, '').strip()
                            result['line'] = clean_line(line)
                            # DAW result['location'] = clean_line(line)
                            return result
            # No state found, just return the country
            line = line.replace(country, '').strip()
            result['line'] = clean_line(line)
            # DAW result['location'] = clean_line(line)
            return result

    print(f"BOB 2.0 - Line: {line}")
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
            if state and state in line:  # Skip empty strings
                pos = line.find(state)
                if pos != -1 and pos < earliest_state_pos:
                    earliest_state_pos = pos
                    earliest_state = state
                    earliest_country = country
                    earliest_state_text = state

        # Check state variations
        if 'state_variations' in info:
            for variation, full_state in info['state_variations'].items():
                if variation and variation in line:  # Skip empty strings
                    pos = line.find(variation)
                    if pos != -1 and pos < earliest_state_pos:
                        earliest_state_pos = pos
                        earliest_state = full_state
                        earliest_country = country
                        earliest_state_text = variation

    print(f"BOB 2.1 - earliest_state_pos: {earliest_state_pos}")
    print(f"BOB 2.2 - earliest_state: {earliest_state}")
    print(f"BOB 2.3 - earliest_country: {earliest_country}")
    print(f"BOB 2.4 - earliest_state_text: {earliest_state_text}")
    print(f"BOB 2.5 - line: {line}")
    # If we found a state, use the earliest one
    if earliest_state is not None:
        result['state'] = earliest_state
        result['country'] = earliest_country
        # Remove the state and country from the line
        line = line.replace(earliest_state_text, '').strip()
        print(f"BOB 2.6 - line: {line}")
        line = line.replace(earliest_country, '').strip()
        print(f"BOB 2.7 - line: {line}")
        result['line'] = clean_line(line)
        print(f"BOB 2.8 - result(line): {result['line']}")
        # DAW result['location'] = clean_line(line)
        return result

    print(f"BOB 3.0 - Line: {line}")
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
                                    # DAW result['location'] = clean_line(line)
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
                    # DAW result['location'] = clean_line(line)
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
                        # DAW result['location'] = clean_line(line)
                        return result
            
            # If we found a country but no state, return the country
            result['country'] = country
            # Remove the country from the line
            line = line.replace(country, '').strip()
            result['line'] = clean_line(line)
            # DAW result['location'] = clean_line(line)
            return result
    
    print(f"BOB 4.0 - Line: {line}")
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
                                            # DAW result['location'] = clean_line(line)
                                            return result
                            break
                    
                    result['country'] = country
                    # Remove the variation and country from the line
                    line = line.replace(variation, '').strip()
                    line = line.replace(country, '').strip()
                    result['line'] = clean_line(line)
                    # DAW result['location'] = clean_line(line)
                    return result

    print(f"BOB 5.0 - Line: {line}")
    # If no state or country found, return the original line
    result['line'] = clean_line(line)
    # DAW result['location'] = clean_line(line)
    return result

def handle_convention(line: str, countries: Dict) -> Optional[Dict]:
    """Handle convention patterns."""

    result = {
        'type': 'Convention',
        'country': None,
        'state': None,
        'location': None,
        'note': None,
    }

    if 'convention' not in line.lower() or 'convention photo' in line.lower():
        return None

    # Special case for Australian Workers Convention
    if line.lower().startswith('australian workers convention'):
        result['location'] = 'Workers Convention'
        result['country'] = 'Australia'
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

    state_country_info = get_state_country(line, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    result['location'] = re.sub(r'\s+', ' ', state_country_info['line'])
    if "Convention" not in result['location']:
        result['location'] = f"{result['location']} Convention"

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
        'note': None
    }

    print(f"\n\nBOB SPECIAL MEETING 0.0 - Line: {line}")

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

    print(f"BOB SM 1.0 - Line: {line}")

    # Handle date or note in parentheses at the end
    date_visit_match = re.search(r'\((.*?)\)', line)
    
    date_note = None
    visit_note = None
    if date_visit_match:
        date_visit_note = date_visit_match.group(1).strip()

        # Check if date_visit_note contains a month or season
        month_pattern = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b'
        season_pattern = r'\b(?:Spring|Summer|Fall|Autumn|Winter)\b'
        
        if re.search(month_pattern, date_visit_note, re.IGNORECASE) or re.search(season_pattern, date_visit_note, re.IGNORECASE):
            date_note = date_visit_note
        else:
            visit_note = date_visit_note
        # Remove the parentheses and their contents from the line
        line = re.sub(r'\([^)]*\)', '', line).strip()

    print(f"BOB SM 2.0 - Line: {line}")

    # Remove USA after US states
    for state in countries['United States']['states']:
        line = re.sub(rf'\b{re.escape(state)}\s+USA\b', state, line, flags=re.IGNORECASE)

    print(f"BOB SM 3.0 - Line: {line}")

    # Hard-coded check for Doak's Special Meeting Shed
    doak_match = re.search(r"Doak.*?s", line)
    if doak_match:
        line = line.replace(doak_match.group(0), "Doak's")

    print(f"BOB SM 4.0 - Line: {line}")

    text=line

    # First check if any word in the line is a country with no states
    words = line.split()
    for i, word in enumerate(words):
        for country, info in countries.items():
            if word == country and not info.get('states'):
                result['country'] = country
                # Remove the country from the line
                line = line.replace(country, '').strip()
                #result['line'] = clean_line(line)
                result['note'] = clean_line(line)
                if "Special Meeting" not in result['note']:
                    result['note'] = f"{result['note']} Special Meeting"
                if date_note:
                    result['note'] = date_note + ' ' + result['note']
                if visit_note:
                    result['note'] = result['note'] + " Visiting from " + visit_note
                # return result

    print(f"BOB SM 5.0 - country: {result['country']}")
    print(f"BOB SM 5.1 - note: {result['note']}")
    print(f"BOB SM 5.2 - line: {line}")

    state_country_info = get_state_country(text, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    if state_country_info['location']:
        result['location'] = state_country_info['location']
    
    result['note'] = state_country_info['line']
    if date_note:
        result['note'] = date_note + ' ' + result['note']
    if visit_note:
        result['note'] = result['note'] + " Visiting from " + visit_note

    return result

def add_to_note_list(current_note: str, addition: str) -> str:
    """Add text to a note, handling the special case of 'Workers List:'."""
    if current_note == 'Workers List:':
        return f"{current_note} {addition}"
    return f"{current_note}, {addition}"

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

    # Handle Winter/Spring pattern with asterisks
    if "*Winter/Spring" in line and "*Winter/Spring*" not in line:
        line = line.replace("*Winter/Spring", "*Winter/Spring*")

    if "Manitoba and Northwest Ontario" in line:
        line = line.replace("Manitoba and Northwest Ontario", "Manitoba/Northwest Ontario")

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
        'note': 'Workers List:'
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

    # Remove month names and their variations first
    month_pattern = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|Autumn)(?:\s*[-–\/]\s*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|Autumn))?\s'
    month_match = re.match(month_pattern, text_before, flags=re.IGNORECASE)
    if month_match:
        matched_month = month_match.group(0).strip()
        text_before = re.sub(month_pattern, '', text_before, flags=re.IGNORECASE).strip()
        result['note'] = add_to_note_list(result['note'], f"{matched_month} List")

    # Look for text in parentheses in the text after Workers List
    paren_match = re.search(r'\((.*?)\)', text_after)
    if paren_match:
        note_text = paren_match.group(1).strip()
        # If note starts with "to ", capitalize it as "To "
        if note_text.lower().startswith('to '):
            note_text = 'To ' + note_text[3:]
        # Append to existing note
        result['note'] = add_to_note_list(result['note'], note_text)
        # Remove the parentheses and their contents from the line
        text_after = re.sub(r'\(.*?\)', '', text_after).strip()

    # Look for CCCC text before any asterisked text
    # First find where any asterisked text starts
    asterisk_pos = text_after.find('*')
    if asterisk_pos == -1:
        asterisk_pos = len(text_after)
    
    # Get the text before any asterisks
    text_before_asterisks = text_after[:asterisk_pos].strip()
    
    # Look for "with" patterns at the start
    with_match = re.match(r'^(?:with|With|w/|w/\s+)(.+)$', text_before_asterisks)
    if with_match:
        # If it starts with a "with" pattern, add "With " + the rest
        cccc_text = "With " + with_match.group(1).strip()
    else:
        # If no "with" pattern, use the whole text
        cccc_text = text_before_asterisks
    
    # If we found CCCC text, add it to the note
    if cccc_text:
        # Append to existing note
        result['note'] = add_to_note_list(result['note'], cccc_text)
        # Remove the CCCC text from the line
        text_after = text_after[asterisk_pos:].strip()

    # Look for text between asterisks
    asterisk_match = re.search(r'\*(.*?)\*', text_after)
    if asterisk_match:
        asterisk_text = asterisk_match.group(1).strip()
        # Append to existing note
        result['note'] = add_to_note_list(result['note'], asterisk_text)
        # Remove the asterisks and their contents from the line
        text_after = re.sub(r'\*.*?\*', '', text_after).strip()
    
    # Look for w/ patterns in text after asterisks
    w_with_match = re.search(r'(?:with|With|\bw\/)(?:\s*)([^\s](?:.+?)(?:\s|$))', text_after)
    if w_with_match:
        w_with_text = w_with_match.group(1).strip()
        # Append to existing note
        result['note'] = add_to_note_list(result['note'], f"With {w_with_text}")
        # Remove the matched text from the line
        text_after = re.sub(r'\bw\/([A-Za-z]+ [A-Za-z]+)', '', text_after).strip()
    
    if text_after:
        # Look for date ranges like Jan-Jun
        date_range_match = re.search(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*[-–]\s*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b', text_after)
        if date_range_match:
            date_range = date_range_match.group(0)
            # Append to existing note
            result['note'] = add_to_note_list(result['note'], date_range)
            # Remove the date range from the text
            text_after = re.sub(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*[-–]\s*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b', '', text_after).strip()

    # Check if the text before Workers List is a country or state/province
    found_country = None
    found_state = None
    remaining_text = text_before

    state_country_info = get_state_country(text_before, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    text_before = state_country_info['line']

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
        'month': None
    }

    # Remove the "Started in the work" text and any surrounding characters
    line = re.sub(r'(?:\*+|\(|\s*,)?\s*Started\s+in\s+the\s+work\s*(?:\*+|\))?', '', line, flags=re.IGNORECASE).strip()

    # Check for date pattern (e.g., "July 6")
    date_match = re.match(r'^(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*\d*', line, flags=re.IGNORECASE)
    if date_match:
        result['month'] = date_match.group(1)
        line = line[date_match.end():].strip()

    state_country_info = get_state_country(line, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    result['location'] = state_country_info['line']

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
    line = state_country_info['line']

    print(f"\n\nBOB PHOTO country: {result['country']}")
    print(f"BOB state: {result['state']}")
    print(f"BOB location: {result['location']}")
    print(f"BOB line: {line}")

    # Get photo type and remaining line
    photo_type, line = get_photo_type(line)
    if photo_type:
        result['note'] = photo_type

    print(f"JOE note: {result['note']}")
    
    # if line:
    #     result['note'] = result['note'] + ' ' + line

    print(f"GUY note: {result['note']}")

    # If no state/province found, set to Unknown location in United States
    if not result['state']:
        result['location'] = 'Unknown'
        result['country'] = 'United States'

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
        'note': None,
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
    
    result['note'] = line
    return result
   
def handle_location_only(line: str, countries: Dict) -> Optional[Dict]:
    """Handle location only patterns."""

    result = {
        'type': 'Location',
        'country': None,
        'state': None,
        'location': None,
        'note': None
    }

    state_country_info = get_state_country(line, countries)
    if state_country_info['country']:
        result['country'] = state_country_info['country']
    if state_country_info['state']:
        result['state'] = state_country_info['state']
    if state_country_info['location']:
        result['location'] = state_country_info['location']
    if state_country_info['line']:
        result['note'] = state_country_info['line']

    if result['country']:
        return result
    
    if result['country'] or result['state'] or result['location'] or result['note']:
        return result
    
    return None
   
def handle_other(line: str, countries: Dict) -> Optional[Dict]:
    """Handle location only patterns."""
    return None
    if 'OTHER' in line.lower():
        return {
            'type': 'Other',
            'location': None,
            'note': None,
            'state': None,
            'country': None
        }
    return None

def process_text_patterns(line: str) -> Dict:
    """Process text patterns and extract relevant information."""
    result = {
        'type': None,
        'country': None,
        'state': None,
        'location': None,
        'note': None,
        'original_text': line,
        'start_date': None,
        'end_date': None,
    }

    # Clean up the line by removing "Visited" and "for"
    line = re.sub(r'^Visited\s+', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s+for\s+', ' ', line, flags=re.IGNORECASE)
    # Remove trailing commas after Meeting or Convention
    line = re.sub(r'((?:Meeting|Convention))\s*,\s*$', r'\1', line, flags=re.IGNORECASE)

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

    return line

def process_file(filepath: str, validate_mode: bool = False, header_output: bool = False) -> None:
    """Process a single file and update the database or just look at patterns."""
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

            line = text_fixes(line)
                    
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
                    pattern_result = process_text_patterns(text_after_year)
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
                                'Original Text'
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
                            pattern_result.get('original_text') or ''
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
    parser = argparse.ArgumentParser(description='Process location files and update database')
    parser.add_argument('--file', type=str, help='Process a single file by name')
    parser.add_argument('--validate', action='store_true', help='Validate mode - process patterns without database interaction')
    args = parser.parse_args()

    input_dir = 'inputs'
    
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