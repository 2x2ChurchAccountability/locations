import math
import re
import countries_data
from collections import defaultdict
import argparse
# ANSI color codes
YELLOW = '\033[93m'
RESET = '\033[0m'

# Global flags for command line options
args = None

def print_deduped_data(data_structure):
    """
    Print the data structure with deduplicated locations in country|state|location format
    Args:
        data_structure (dict): The nested dictionary containing the data
    """
    for country, states in sorted(data_structure.items()):
        for state, locations in sorted(states.items()):
            for location in sorted(locations):
                print(f"{country}|{state}|{location}")

def parse_args():
    """
    Parse command line arguments and set global flags
    """
    global args
    parser = argparse.ArgumentParser(description='Process location data with various output options')
    parser.add_argument('--detail', action='store_true', help='Show detailed processing information')
    parser.add_argument('--deduped', action='store_true', help='Show deduplicated location data')
    parser.add_argument('--countries', action='store_true', help='Show countries data structure')
    
    args = parser.parse_args()
    
    # If no arguments provided, default to --detail
    if not any([args.detail, args.deduped, args.countries]):
        args.detail = True

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

def get_tabsXX(input_str):
    """
    Returns a string of tab characters based on input string length
    Args:
        input_str (str): The input string to measure
    Returns:
        str: A string of tab characters
    """
    length = len(input_str)
    tab_count = max(1, (length - 32) // 4)
    return '\t' * tab_count

def get_tabcount(string):
    tab_width=8
    max_length=50
    
    max_tab_stops = math.ceil(max_length / tab_width)
    results = []
    current_tab_stops = math.ceil(len(string)/ tab_width)
    padding_tabs = max_tab_stops - current_tab_stops
    return padding_tabs

def get_tabs(string):
    return '\t' * get_tabcount(string)

def add_note(the_note, after_params):
    """
    Combines the_note and after_params with a comma if the_note is non-blank
    Args:
        the_note (str): The existing note
        after_params (str): The additional text to append
    Returns:
        str: Combined note with comma if needed
    """
    if not the_note:
        return after_params
    return f"{the_note}, {after_params}"

def process_line(line, line_number, data_structure):
    """
    Process a single line from the file and store in data structure
    Args:
        line (str): The line to process
        line_number (int): The line number in the file
        data_structure (dict): The nested dictionary to store the data
    Returns:
        tuple: (length of the_front, length of everything_else)
    """

    original_line = line
    removed_text = []

    the_country = ""
    country_variation = ""

    # Step 1: Remove month patterns
    single_month_pattern = r'^(?:Jan(?:uary)?\b|Feb(?:ruary)?\b|Mar(?:ch)?\b|Apr(?:il)?\b|May\b|Jun(?:e)?\b|Jul(?:y)?\b|Aug(?:ust)?\b|Sep(?:t(?:ember)?)?\b|Oct(?:ober)?\b|Nov(?:ember)?\b|Dec(?:ember)?\b|Autumn\b|Spring\b)\.?\s*'
    range_month_pattern = r'^(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*[-/]\s*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b'

    # Skip over month patterns and capture removed text
    def capture_removed(match):
        removed_text.append(match.group(0))
        return ''

    # First remove the range patterns
    line = re.sub(range_month_pattern, capture_removed, line)
    # Then remove the single month patterns
    line = re.sub(single_month_pattern, capture_removed, line)
    
    # Strip any extra whitespace that might be left after removing the patterns
    line = line.strip()
    
    # Skip if line is empty after pattern removal
    if not line:
        return 0, 0
        
    # Check if any patterns were removed
    pattern_removed = line != original_line.strip()
    
    # Step 2: Split line into front and tail at "Workers List"
    workers_list_pattern = r'^(.*?)Workers List(.*)$'
    match = re.match(workers_list_pattern, line, re.IGNORECASE)
    if match:
        the_front = match.group(1).strip()
        the_tail = match.group(2).strip()
        line = the_tail  # Keep only the tail for further processing
    else:
        the_front = ""
        the_tail = line

    if 'Ontario and Quebec' in the_front:
        the_front = the_front.replace('Ontario and Quebec', 'Ontario/Quebec')
    if 'Saskatchewan and MB' in the_front:
        the_front = the_front.replace('Saskatchewan and MB', 'Saskatchewan/Manitoba')
    if 'NWOntario' in the_front:
        the_front = the_front.replace('NWOntario', 'Northwest Ontario')
    if 'Manitoba/NW Ontario' in the_front:
        the_front = the_front.replace('Manitoba/NW Ontario', 'Manitoba/Northwest Ontario')
    if 'Ohio and West Virginia' in the_front:
        the_front = the_front.replace('Ohio and West Virginia', 'Ohio/West Virginia')
    if 'W. Virginia' in the_front:
        the_front = the_front.replace('W. Virginia', 'West Virginia')
    if 'Colorado and Utah' in the_front:
        the_front = the_front.replace('Colorado and Utah', 'Colorado/Utah')
    if 'Indiana and Illinois' in the_front:
        the_front = the_front.replace('Indiana and Illinois', 'Indiana/Illinois')
    if 'Oregon and S. Idaho' in the_front:
        the_front = the_front.replace('Oregon and S. Idaho', 'Oregon/S. Idaho')
    if 'S. Idaho' in the_front:
        the_front = the_front.replace('S. Idaho', 'South Idaho')
    if 'N. Wyoming' in the_front:
        the_front = the_front.replace('N. Wyoming', 'North Wyoming')
    if 'N. Carolina' in the_front:
        the_front = the_front.replace('N. Carolina', 'North Carolina')
        
    
    # Step A: Extract the country using countries from countries_data.py

    if the_front:
        # Special case for British Columbia to avoid Columbia match
        if "British Columbia" in the_front:
            the_country = "Canada"
        else:
            # First try to find a country by name or its variations
            for country_name, country_info in countries_data.countries.items():
                # Check the main country name - handle different separators
                if ' and ' in country_name:
                    # For combined countries with 'and', check for exact match first
                    if country_name in the_front:
                        the_country = country_name
                        break
                elif '/' in country_name:
                    # For combined countries with forward slashes, require exact match
                    if country_name in the_front:
                        the_country = country_name
                        break
                else:
                    # Regular country name check
                    if re.search(r'(?:^|\s)' + re.escape(country_name) + r'(?:\s|$)', the_front):
                        the_country = country_name
                        break
                # Check variations if they exist
                if 'variations' in country_info:
                    for variation in country_info['variations']:
                        if re.search(r'(?:^|\s)' + re.escape(variation) + r'(?:\s|$)', the_front):
                            the_country = country_name
                            country_variation = variation
                            break
                    if the_country:
                        break
        
        # If no country found, look for a state match
        if not the_country:
            # Split the_front into words by both space and /
            words = []
            for part in the_front.split():
                words.extend(part.split('/'))
            # Try combinations of 1 to 3 consecutive words
            for i in range(len(words)):
                for j in range(1, min(4, len(words) - i + 1)):
                    potential_state = ' '.join(words[i:i+j])
                    for country_name, country_info in countries_data.countries.items():
                        # Check if the state exists in the country's states list
                        if 'states' in country_info and potential_state in country_info['states']:
                            the_country = country_name
                            break
                        # Check if the state exists in the country's state variations
                        if 'state_variations' in country_info and potential_state in country_info['state_variations']:
                            the_country = country_name
                            break
                    if the_country:
                        break
                if the_country:
                    break

    if the_country:
        the_front = the_front.replace(the_country, '')
        if 'Australia' in the_front:
            the_front = the_front.replace('Australia', '')
        the_front = the_front.strip()
        if the_front.startswith(','):
            the_front = the_front[1:].strip()

    if country_variation:
        the_front = the_front.replace(country_variation, '').strip()

    # Step 3: Extract content from parentheses and the note
    in_parens = ""
    after_parens = the_tail
    parens_pattern = r'^\((.*?)\)(.*)$'
    match = re.match(parens_pattern, the_tail)
    if match:
        in_parens = match.group(1).strip()
        after_parens = match.group(2).strip()
    else:
        match2 = re.search(r'(.*?)\((.*?)\)(.*)', the_tail)

        if match2:
            if len(the_front) and the_front in match2.group(1):
                in_parens = match2.group(2).strip()
                after_parens = match2.group(3).strip()
            elif "Newfoundland" in match2.group(1):
                the_front = "Newfoundland and Labrador"
                in_parens = match2.group(2).strip()
                after_parens = match2.group(3).strip()
            elif "Adjustments" in match2.group(1):
                in_parens = match2.group(1).strip() + ' ' + match2.group(2).strip()
                after_parens = match2.group(3).strip()
            elif "New Brunswick" in match2.group(1):
                in_parens = "to " + match2.group(2).strip()
                after_parens = match2.group(3).strip()
            else:
                in_parens = "bob"
                after_parens = "sue"

        #formulate my_output showing all the pieces of match and their index
        #my_output = f"{the_front} | {the_tail} | {in_parens} | {after_parens} | MATCH: (1){match2.group(1)} | (2){match2.group(2)} | (3){match2.group(3)}"
        #print(my_output)
    #return len(the_front), len(after_parens)

    # Step 4:  Places that aren't places
    #   in_parens starts with 'to ' or 'care of' or 'helping' or return home' or 'home' or 'campanion later' or 'new worker'
    #   or it contains the term 'pro tem'
    special_case_phrase = ""
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
        everything_else = in_parens[4:].strip()
    elif in_parens.lower().startswith('visiting '):
        special_case_phrase = 'visiting'
        everything_else = in_parens[8:].strip()
    elif in_parens.lower().startswith('home'):
        special_case_phrase = 'home'
        everything_else = in_parens[4:].strip()
    elif in_parens.lower().startswith('field campanion later'):
        special_case_phrase = 'field campanion later'
        everything_else = in_parens[21:].strip()
    elif in_parens.lower().startswith('campanion later'):
        special_case_phrase = 'campanion later'
        everything_else = in_parens[14:].strip()
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

    the_field = '--Not Specified--'
    the_note = ""
    if special_case_phrase:
        if special_case_phrase == 'pro tem':
            the_note =  everything_else.strip() + ' pro tem'
        elif special_case_phrase == 'to pro tem':
            the_note = 'To ' + everything_else.strip() + ' pro tem'
        else:
            the_note = upper_words(special_case_phrase) + ' ' + everything_else.strip()
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
            the_note = "Field: " + in_parens
    
    #Step 5: Process the after_parens.  Two special cases:  'with ' or 'w/ ' or 'w/' and 'overseer' and *month*
    
    if special_case_phrase == 'overseer':
        if "overseer" not in after_parens.lower():
            if after_parens:
                after_parens += ', Overseer'
            else:
                after_parens = 'Overseer'
                
    if after_parens:
        # if after_parens contains 'with ', 'w/ ' or 'w/'
        if 'with ' in after_parens.lower() or 'w/ ' in after_parens.lower() or 'w/' in after_parens.lower():
            #use regex to replace 'with ' or 'w/ ' or 'w/' with 'Companion: '
            after_parens = re.sub(r'(with |w/ |w/$)', 'Companion: ', after_parens)
        if "overseer" in after_parens.lower():
            after_parens = re.sub(r'overseer', 'Overseer', after_parens)
        the_note = add_note(the_note, after_parens)

        if "first year in the work" in after_parens.lower():
            the_note = add_note(the_note, "New Worker")

        # if after_parens contains a Jul, *Jul*, *Spring*, *Autumn*, *Spring*, *Summer*, *Winter-Spring*, *Aug-Dec*, Jul/Dec
        if re.search(r'\b(Jul|Spring|Autumn|Summer|Winter-Spring|Aug-Dec|Jul/Dec)\b', after_parens):
            some_periods = re.sub(r'\b(Jul|Spring|Autumn|Summer|Winter-Spring|Aug-Dec|Jul/Dec)\b', 'Month: ', after_parens)

    
    the_field = re.sub(r'\bN\.?\s+', 'North ', the_field)
    the_field = re.sub(r'\bS\.?\s+', 'South ', the_field)
    the_field = re.sub(r'\bE\.?\s+', 'East ', the_field)
    the_field = re.sub(r'\bW\.?\s+', 'West ', the_field)
    the_field = re.sub(r'\bNW\.?\s+', 'Northwest ', the_field)
    the_field = re.sub(r'\bNE\.?\s+', 'Northeast ', the_field)
    the_field = re.sub(r'\bSW\.?\s+', 'Southwest ', the_field)    
    the_field = re.sub(r'\bSE\.?\s+', 'Southeast ', the_field)

    the_field = re.sub(r'\sN\.?$', ' North', the_field)
    the_field = re.sub(r'\sS\.?$', ' South', the_field)
    the_field = re.sub(r'\sE\.?$', ' East', the_field)
    the_field = re.sub(r'\sW\.?$', ' West', the_field)
    the_field = re.sub(r'\sNW\.?$', ' Northwest', the_field)
    the_field = re.sub(r'\sNE\.?$', ' Northeast', the_field)
    the_field = re.sub(r'\sSW\.?$', ' Southwest', the_field)
    the_field = re.sub(r'\sSE\.?$', ' Southeast', the_field)
    
    # Split by slashes with optional whitespace around them
    parts = re.split(r'\s*/\s*', the_field)
    # Join with comma and space
    the_field = ', '.join(parts)


    # Instead of printing, store in data structure
    country = the_country if the_country else '--No Country--'
    state = the_front if len(the_front) else '--No State--'
    location = the_field

    if args.detail:
        print(f"{country}|{state}|{location}|{the_note}|{original_line}")
    
    # Create nested structure if it doesn't exist
    if country not in data_structure:
        data_structure[country] = {}
    
    # Create state dictionary if it doesn't exist
    if state not in data_structure[country]:
        data_structure[country][state] = set()
    
    # Add the location to the state (set automatically handles deduplication)

    data_structure[country][state].add(location)
    
    return len(the_front), len(everything_else)

def print_countries(data_structure):
    """
    Print the data structure in sorted order with pipe separators
    Args:
        data_structure (dict): The nested dictionary containing the data
    """
    def word_count_sort_key(text):
        # Count words considering both spaces and forward slashes as delimiters
        word_count = len(re.split(r'[\s/]+', text))
        # Return tuple for sorting - word count first (negative for reverse sort), then alphabetical
        return (-word_count, text)

    print('"""Data structure containing country information including states, variations, and cities."""')

    print("\ncountries = {")

    # Sort countries by word count and then alphabetically
    sorted_countries = sorted(data_structure.keys(), key=word_count_sort_key)
    
    for country in sorted_countries:
        country_info = data_structure[country]
        print(f"   '{country}': {{")
        print(f"      'name': '{country_info['name']}',")
        
        # Print states if they exist
        if 'states' in country_info:
            print("      'states': [")
            # Sort states by word count and then alphabetically
            states = sorted(country_info['states'], key=word_count_sort_key)
            
            # Group states by word count
            current_word_count = None
            current_line_states = []
            
            for state in states:
                word_count = len(re.split(r'[\s/]+', state))
                
                # If word count changes, print current line and start new line
                if current_word_count is not None and word_count != current_word_count:
                    if current_line_states:
                        print("        " + ", ".join(f"'{state}'" for state in current_line_states) + ",")
                        current_line_states = []
                
                current_word_count = word_count
                current_line_states.append(state)
                
                # Print line when we have 7 states
                if len(current_line_states) == 7:
                    print("        " + ", ".join(f"'{state}'" for state in current_line_states) + ",")
                    current_line_states = []
            
            # Print any remaining states
            if current_line_states:
                print("        " + ", ".join(f"'{state}'" for state in current_line_states) + ",")
                
            print("      ],")
        
        # Print cities if they exist
        if 'cities' in country_info:
            print("      'cities': {")
            
            # Sort cities by word count and then alphabetically
            city_items = sorted(country_info['cities'].items(), key=lambda x: word_count_sort_key(x[0]))
            
            # Group cities by word count
            current_word_count = None
            current_cities = []
            
            for city, state in city_items:
                word_count = len(re.split(r'[\s/]+', city))
                
                # If word count changes, print current cities and start new group
                if current_word_count is not None and word_count != current_word_count:
                    for c, s in current_cities:
                        escaped_city = c.replace("'", "\\'")
                        print(f"        '{escaped_city}': '{s}',")
                    if word_count != -len(re.split(r'[\s/]+', city_items[-1][0])):  # Don't print newline after last group
                        print("")
                    current_cities = []
                
                current_word_count = word_count
                current_cities.append((city, state))
            
            # Print any remaining cities
            if current_cities:
                for city, state in current_cities:
                    escaped_city = city.replace("'", "\\'")
                    print(f"        '{escaped_city}': '{state}',")
                
            print("      },")
        
        # Print special_location if it exists
        if 'special_location' in country_info:
            print(f"      'special_location': '{country_info['special_location']}',")
        
        # Print variations if they exist
        if 'variations' in country_info:
            print("      'variations': [")
            print("        " + ", ".join(f"'{var}'" for var in sorted(country_info['variations'])))
            print("      ],")
        
        # Print state_variations if they exist
        if 'state_variations' in country_info:
            print("      'state_variations': {")
            # Sort state variations by code and print each on a new line with comma
            sorted_variations = sorted(country_info['state_variations'].items())
            for i, (var, full) in enumerate(sorted_variations):
                # Add comma if not the last item
                comma = "," if i < len(sorted_variations) - 1 else ""
                print(f"        '{var}': '{full}'{comma}")
            print("      },")
            
        print("   },")
    print("}")

def update_countries_data(data_structure):
    """
    Update the countries data structure with new information from data_structure.
    Args:
        data_structure (dict): The nested dictionary containing the new data
    """
    def slash_sort_key(state):
        # Count the number of slashes in the state name
        slash_count = state.count('/')
        # Return a tuple where first element is negative slash count (so higher counts come first)
        # and second element is the state name for alphabetical sorting within same slash count
        return (-slash_count, state)

    def word_count_sort_key(country):
        # Return a tuple where first element is negative word count (so higher counts come first)
        # and second element is the country name for alphabetical sorting within same word count
        return (-len(country.split()), country)

    # Step 1: Add any missing countries
    for country in data_structure:
        if country not in countries_data.countries:
            countries_data.countries[country] = {
                'name': country,
                'states': [],
                'cities': {}
            }
    
    # Step 2: Add any missing states and cities
    for country, states in data_structure.items():
        country_info = countries_data.countries[country]
        
        # Add any missing states
        for state in states:
            if state not in country_info['states']:
                country_info['states'].append(state)
        
        # Add any missing cities
        for state, cities in states.items():
            for city in cities:
                if city not in country_info['cities']:
                    # If state is blank or empty string, use "--No State--"
                    effective_state = state if state and state.strip() else "--No State--"
                    country_info['cities'][city] = effective_state
                    # Ensure "--No State--" exists in states list if needed
                    if effective_state == "--No State--" and effective_state not in country_info['states']:
                        country_info['states'].append(effective_state)
    
    # Step 3: Fix any existing cities with empty states
    for country_info in countries_data.countries.values():
        # Fix any cities with empty states
        for city, state in list(country_info['cities'].items()):
            if not state or not state.strip():
                country_info['cities'][city] = "--No State--"
                if "--No State--" not in country_info['states']:
                    country_info['states'].append("--No State--")
    
    # Step 4: Sort and organize the data
    # First, sort countries by word count and then alphabetically
    countries_data.countries = dict(sorted(countries_data.countries.items(), key=lambda x: word_count_sort_key(x[0])))
    
    for country_info in countries_data.countries.values():
        # Sort states by slash count and then alphabetically
        country_info['states'].sort(key=slash_sort_key)
        
        # Sort cities by state then city name
        # First, create a list of tuples (state, city) for sorting
        city_tuples = [(state, city) for city, state in country_info['cities'].items()]
        city_tuples.sort()  # This sorts by state first, then city
        
        # Reconstruct the cities dictionary in sorted order
        country_info['cities'] = {city: state for state, city in city_tuples}
        
        # Sort state_variations by code if they exist
        if 'state_variations' in country_info:
            country_info['state_variations'] = dict(sorted(country_info['state_variations'].items()))

def process_wl_file():
    try:
        # Initialize the data structure as a simple dictionary
        data_structure = {}
        
        max_front_length = 0
        max_everything_else_length = 0
        
        with open('wl.txt', 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                # Remove trailing whitespace and newlines
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                    
                # Process each line using the process_line function
                front_length, everything_else_length = process_line(line, line_number, data_structure)
                if front_length > max_front_length:
                    max_front_length = front_length
                if everything_else_length > max_everything_else_length:
                    max_everything_else_length = everything_else_length
        
        # Handle output based on command line flags
        if not args.detail:
            update_countries_data(data_structure)
            if args.countries:
                print_countries(countries_data.countries)
            if args.deduped:
                print_deduped_data(data_structure)
                
    except FileNotFoundError:
        print("Error: wl.txt file not found")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    parse_args()
    process_wl_file()
