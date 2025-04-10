import countries_data
import uuid
import os
import csv
import argparse
import sys

# Global variables
SCHEMA = 'test'  # Change this to switch between schemas (e.g., 'public', 'test', 'dev')

def debug(message):
    """Write debug message to stderr if debug mode is enabled."""
    if args.debug:
        print(f"DEBUG: {message}", file=sys.stderr)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Generate SQL insert statements for countries, states, and locations.')
parser.add_argument('--debug', action='store_true', help='Enable debug output')
args = parser.parse_args()

def generate_guid(prefix, sequence):
    """Generate a GUID in the specified format."""
    base = f"20250407-{prefix}-{prefix}-{prefix}-{prefix}{prefix}"
    return f"{base}{sequence:04d}"

def escape_single_quotes(text):
    """Escape single quotes in text for SQL."""
    return text.replace("'", "''")

def load_existing_records():
    """Load existing records from CSV files."""
    existing = {
        'countries': {},
        'states': {},
        'locations': {},
        'curr_countries': {},  # Store curr_countries data
        'curr_states': {},     # Store curr_states data
        'curr_locations': {}   # Store curr_locations data
    }
    
    # Load curr_countries
    with open('curr_countries.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up the column names by removing quotes and BOM
            clean_row = {k.strip('"').strip('\ufeff'): v.strip('"') for k, v in row.items()}
            existing['curr_countries'][clean_row['recid']] = {
                'name': clean_row['name'],
                'recid': clean_row['recid']
            }
    
    # Load curr_states
    with open('curr_states.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up the column names by removing quotes and BOM
            clean_row = {k.strip('"').strip('\ufeff'): v.strip('"') for k, v in row.items()}
            existing['curr_states'][clean_row['recid']] = {
                'name': clean_row['name'],
                'recid': clean_row['recid'],
                'country_recid': clean_row['country_recid']
            }
    
    # Load curr_locations
    with open('curr_locations.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up the column names by removing quotes and BOM
            clean_row = {k.strip('"').strip('\ufeff'): v.strip('"') for k, v in row.items()}
            existing['curr_locations'][clean_row['recid']] = {
                'name': clean_row['name'],
                'recid': clean_row['recid'],
                'state_recid': clean_row['state_recid']
            }
            existing['locations'][clean_row['name']] = clean_row['recid']
    
    return existing

def write_countries(existing):
    """Generate and write country insert statements."""
    sequence = 1
    with open('inserts_country.sql', 'w') as f:
        # First write all existing countries from CSV as comments
        for country_name, recid in existing['countries'].items():
            escaped_name = escape_single_quotes(country_name)
            f.write(f"-- INSERT INTO {SCHEMA}.country (recid, name) VALUES ('{recid}', '{escaped_name}');\n")
        
        # Then handle countries from countries_data
        for country_name in countries_data.countries:
            escaped_name = escape_single_quotes(country_name)
            
            # Skip if country already exists (we already wrote it as a comment)
            if country_name in existing['countries']:
                continue
            
            # Generate new country
            recid = generate_guid('cccc', sequence)
            state_insert = f"INSERT INTO {SCHEMA}.country (recid, name) VALUES ('{recid}', '{escaped_name}');\n"
            f.write(state_insert)
            # Store the newly generated recid to ensure consistency
            existing['countries'][country_name] = recid
            sequence += 1

def write_states(existing):
    """Generate and write state insert statements."""
    sequence = 1
    with open('inserts_state.sql', 'w') as f:
        # First write all existing states from CSV as comments
        for (country_recid, state_name), state_recid in existing['states'].items():
            escaped_name = escape_single_quotes(state_name)
            f.write(f"-- INSERT INTO {SCHEMA}.state (recid, country_recid, name) VALUES ('{state_recid}', '{country_recid}', '{escaped_name}');\n")
        
        # Then handle states from countries_data
        for country_name, country_data in countries_data.countries.items():
            # Get the country's recid (same format as in write_countries)
            country_recid = existing['countries'].get(country_name, 
                generate_guid('cccc', list(countries_data.countries.keys()).index(country_name) + 1))
            
            for state_name in country_data['states']:
                # Replace --No State-- with country name
                if state_name == '--No State--':
                    state_name = country_name
                
                escaped_name = escape_single_quotes(state_name)
                key = (country_recid, state_name)
                
                # Skip if state already exists (we already wrote it as a comment)
                if key in existing['states']:
                    continue
                
                # Generate new state
                recid = generate_guid('dddd', sequence)
                f.write(f"INSERT INTO {SCHEMA}.state (recid, country_recid, name) VALUES ('{recid}', '{country_recid}', '{escaped_name}');\n")
                # Store the state key in existing['states']
                existing['states'][key] = recid
                sequence += 1

def write_location_mapping(mappings):
    """Write all mappings between old and new location records to a CSV file."""
    mapping_file = 'inserts_location_mapping.csv'
    
    # Write all mappings at once
    with open(mapping_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(['location_name', 'old_recid', 'new_recid'])
        for location_name, old_recid, new_recid in mappings:
            writer.writerow([location_name, old_recid, new_recid])

def write_perp_location_updates(mappings):
    """Write update statements for perp_location table."""
    with open('inserts_perp_location.sql', 'w') as f:
        for location_name, old_recid, new_recid in mappings:
            f.write(f"update {SCHEMA}.perp_location set location_recid='{new_recid}' where location_recid='{old_recid}';\n")

def process_exception_mappings(existing, generated_locations, sequence):
    """Process locations that weren't mapped and try to find matching states."""
    exceptions = []
    with open('inserts_exception_mapping.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(['location_name', 'old_recid', 'status', 'new_recid', 'state_recid'])
        
        # Get all state names and their recids
        state_mapping = {}
        for (country_recid, state_name), state_recid in existing['states'].items():
            state_mapping[state_name] = state_recid
        
        # Process each location from curr_locations.csv
        for location_name, old_recid in existing['locations'].items():
            # Skip if this location was already processed
            if location_name in generated_locations:
                continue
                
            # Look for a state with the same name
            if location_name in state_mapping:
                # Found a matching state, create new location record
                new_recid = generate_guid('eeee', sequence)
                state_recid = state_mapping[location_name]
                writer.writerow([location_name, old_recid, 'FOUND', new_recid, state_recid])
                exceptions.append((new_recid, state_recid, location_name, old_recid))
                sequence += 1
            else:
                # No matching state found
                writer.writerow([location_name, old_recid, 'NOT FOUND', '', ''])
    
    # Write the insert statements for found exceptions
    if exceptions:
        with open('inserts_location.sql', 'a') as f:
            f.write('\n-- Exception locations\n')
            for new_recid, state_recid, location_name, _ in exceptions:
                escaped_name = escape_single_quotes(location_name)
                f.write(f"INSERT INTO {SCHEMA}.location (recid, state_recid, name) VALUES ('{new_recid}', '{state_recid}', '{escaped_name}');\n")
        
        # Write perp_location updates for exceptions
        with open('inserts_perp_location.sql', 'a') as f:
            f.write('\n-- Exception location updates\n')
            for new_recid, _, _, old_recid in exceptions:
                f.write(f"update {SCHEMA}.perp_location set location_recid='{new_recid}' where location_recid='{old_recid}';\n")
    
    return sequence

def process_not_found_locations(existing, generated_locations, generated_states, generated_countries, country_sequence, state_sequence):
    """Process locations that weren't found and generate necessary insert statements."""
    not_found_locations = []
    not_found_states = set()
    not_found_countries = set()
    
    # First pass: collect all NOT FOUND locations and their state info
    for location_name, old_recid in existing['locations'].items():
        # Skip if this location was already processed in generated_locations
        if location_name in generated_locations:
            continue
            
        location_data = existing['curr_locations'].get(old_recid)
        if not location_data:
            continue
            
        state_recid = location_data['state_recid']
        state_data = existing['curr_states'].get(state_recid)
        if not state_data:
            continue
            
        # Check if this location was already processed in exception mappings
        location_exists = False
        try:
            with open('inserts_exception_mapping.csv', 'r') as f:
                reader = csv.DictReader(f, delimiter='|')
                for row in reader:
                    if row['location_name'] == location_name and row['status'] == 'FOUND':
                        location_exists = True
                        break
        except FileNotFoundError:
            pass  # File doesn't exist yet, so no exceptions have been processed
        
        if location_exists:
            continue
            
        # Step 1: Try to find matching state
        state_name = state_data['name']
        new_state_recid = None
        
        # First check if state exists in existing states
        state_exists = False
        for (country_recid, existing_state_name), existing_state_recid in existing['states'].items():
            if existing_state_name == state_name:
                new_state_recid = existing_state_recid
                state_exists = True
                break
        
        # If not found in existing states, check generated states
        if not state_exists and state_name in generated_states:
            new_state_recid = generated_states[state_name]
            state_exists = True
        
        # If still not found, generate new state
        if not state_exists:
            new_state_recid = generate_guid('dddd', state_sequence)
            state_sequence += 1
            not_found_states.add(state_recid)
            state_data['new_state_recid'] = new_state_recid
            
        not_found_locations.append({
            'name': location_name,
            'old_recid': old_recid,
            'state_recid': new_state_recid,
            'state_name': state_name,
            'original_state_recid': state_recid
        })
    
    # Second pass: process states that weren't found
    for state_recid in not_found_states:
        state_data = existing['curr_states'].get(state_recid)
        if not state_data:
            continue
            
        country_recid = state_data['country_recid']
        country_data = existing['curr_countries'].get(country_recid)
        if not country_data:
            continue
            
        # Step 2: Try to find matching country
        country_name = country_data['name']
        new_country_recid = None
        
        # Special case: If country is "Southern Alberta", use Canada's recid
        if country_name == "Southern Alberta":
            country_name = "Canada"
            # Find Canada's recid in generated_countries
            for name, recid in generated_countries.items():
                if name == "Canada":
                    new_country_recid = recid
                    break
        elif country_name in generated_countries:
            new_country_recid = generated_countries[country_name]
        else:
            new_country_recid = generate_guid('cccc', country_sequence)
            country_sequence += 1
            not_found_countries.add(country_recid)
            country_data['new_country_recid'] = new_country_recid
            
        # Store state info for later use
        state_data['new_country_recid'] = new_country_recid
        state_data['country_name'] = country_name
        state_data['original_country_recid'] = country_recid
    
    # Write all insert statements to their respective files
    # Step 3: Write country inserts first
    with open('inserts_country.sql', 'a') as f:
        f.write('\n-- NOT FOUND Countries\n')
        # Sort countries by recid
        sorted_countries = sorted(not_found_countries, key=lambda x: existing['curr_countries'][x]['new_country_recid'])
        for country_recid in sorted_countries:
            country_data = existing['curr_countries'].get(country_recid)
            if country_data:
                escaped_name = escape_single_quotes(country_data['name'])
                f.write(f"INSERT INTO {SCHEMA}.country (recid, name) VALUES ('{country_data['new_country_recid']}', '{escaped_name}');\n")
    
    # Step 2: Write state inserts
    with open('inserts_state.sql', 'a') as f:
        f.write('\n-- NOT FOUND States\n')
        # Sort states by recid
        sorted_states = sorted(not_found_states, key=lambda x: existing['curr_states'][x]['new_state_recid'])
        for state_recid in sorted_states:
            state_data = existing['curr_states'].get(state_recid)
            if state_data:
                escaped_name = escape_single_quotes(state_data['name'])
                f.write(f"INSERT INTO {SCHEMA}.state (recid, country_recid, name) VALUES ('{state_data['new_state_recid']}', '{state_data['new_country_recid']}', '{escaped_name}');\n")
    
    # Step 1: Write location inserts
    with open('inserts_location.sql', 'a') as f:
        f.write('\n-- NOT FOUND Locations\n')
        # Sort locations by recid
        sorted_locations = sorted(not_found_locations, key=lambda x: x['old_recid'])
        for loc in sorted_locations:
            escaped_name = escape_single_quotes(loc['name'])
            f.write(f"INSERT INTO {SCHEMA}.location (recid, state_recid, name) VALUES ('{loc['old_recid']}', '{loc['state_recid']}', '{escaped_name}');\n")
    
    return country_sequence, state_sequence

def write_locations(existing):
    """Generate and write location insert statements."""
    sequence = len(existing['locations']) + 1  # Start after existing locations
    mappings = []  # List to collect all mappings
    generated_locations = set()  # Track all location names we generate
    generated_states = {}  # Track state names and their recids
    generated_countries = {}  # Track country names and their recids
    state_sequence = len(existing['states']) + 1  # Start after existing states
    
    with open('inserts_location.sql', 'w') as f:
        # Then handle locations from countries_data
        for country_name, country_data in countries_data.countries.items():
            # Get the country's recid from existing or generate a new one
            country_recid = existing['countries'].get(country_name, 
                generate_guid('cccc', list(countries_data.countries.keys()).index(country_name) + 1))
            generated_countries[country_name] = country_recid
            
            # Handle case where cities list is empty
            if not country_data['cities']:
                # If no states listed, create state and location using country name
                if not country_data['states']:
                    state_name = country_name
                    state_key = (country_recid, state_name)
                    if state_key not in existing['states']:
                        state_recid = generate_guid('dddd', state_sequence)
                        existing['states'][state_key] = state_recid
                        generated_states[state_name] = state_recid
                        with open('inserts_state.sql', 'a') as state_file:
                            escaped_name = escape_single_quotes(state_name)
                            state_file.write(f"INSERT INTO {SCHEMA}.state (recid, country_recid, name) VALUES ('{state_recid}', '{country_recid}', '{escaped_name}');\n")
                        state_sequence += 1
                    state_recid = existing['states'][state_key]
                    
                    # Create location using country name
                    location_key = (state_recid, country_name)
                    if location_key not in existing['locations']:
                        escaped_name = escape_single_quotes(country_name)
                        recid = generate_guid('eeee', sequence)
                        f.write(f"INSERT INTO {SCHEMA}.location (recid, state_recid, name) VALUES ('{recid}', '{state_recid}', '{escaped_name}');\n")
                        generated_locations.add(country_name)
                        # Check if this location name exists in curr_locations.csv
                        if country_name in existing['locations']:
                            mappings.append((country_name, existing['locations'][country_name], recid))
                        sequence += 1
                else:
                    # Create location for each state
                    for state_name in country_data['states']:
                        state_key = (country_recid, state_name)
                        if state_key not in existing['states']:
                            state_recid = generate_guid('dddd', state_sequence)
                            existing['states'][state_key] = state_recid
                            generated_states[state_name] = state_recid
                            with open('inserts_state.sql', 'a') as state_file:
                                escaped_name = escape_single_quotes(state_name)
                                state_file.write(f"INSERT INTO {SCHEMA}.state (recid, country_recid, name) VALUES ('{state_recid}', '{country_recid}', '{escaped_name}');\n")
                            state_sequence += 1
                        state_recid = existing['states'][state_key]
                        
                        # Create location using state name
                        location_key = (state_recid, state_name)
                        if location_key not in existing['locations']:
                            escaped_name = escape_single_quotes(state_name)
                            recid = generate_guid('eeee', sequence)
                            f.write(f"INSERT INTO {SCHEMA}.location (recid, state_recid, name) VALUES ('{recid}', '{state_recid}', '{escaped_name}');\n")
                            generated_locations.add(state_name)
                            # Check if this location name exists in curr_locations.csv
                            if state_name in existing['locations']:
                                mappings.append((state_name, existing['locations'][state_name], recid))
                            sequence += 1
                continue
            
            for city_name, state_names in country_data['cities'].items():
                for state_name in state_names:
                    # Replace --No State-- with country name before any processing
                    if state_name == '--No State--':
                        state_name = country_name
                    
                    # Get the state's recid - use the state name directly from the mapping
                    state_key = (country_recid, state_name)
                    
                    # Get the state_recid from existing states
                    if state_key not in existing['states']:
                        # Create the state on the spot
                        state_recid = generate_guid('dddd', state_sequence)
                        existing['states'][state_key] = state_recid
                        generated_states[state_name] = state_recid
                        # Write the insert statement to the state SQL file
                        with open('inserts_state.sql', 'a') as state_file:
                            escaped_name = escape_single_quotes(state_name)
                            state_file.write(f"INSERT INTO {SCHEMA}.state (recid, country_recid, name) VALUES ('{state_recid}', '{country_recid}', '{escaped_name}');\n")
                        state_sequence += 1
                        
                    state_recid = existing['states'][state_key]
                    
                    # Replace --Not Specified-- with state name
                    if city_name == '--Not Specified--':
                        city_name = state_name
                    
                    escaped_name = escape_single_quotes(city_name)
                    key = (state_recid, city_name)
                    
                    # Skip if location already exists (we already wrote it as a comment)
                    if key in existing['locations']:
                        continue
                    
                    # Generate new location
                    recid = generate_guid('eeee', sequence)
                    f.write(f"INSERT INTO {SCHEMA}.location (recid, state_recid, name) VALUES ('{recid}', '{state_recid}', '{escaped_name}');\n")
                    generated_locations.add(city_name)
                    # Check if this location name exists in curr_locations.csv
                    if city_name in existing['locations']:
                        mappings.append((city_name, existing['locations'][city_name], recid))
                    sequence += 1
    
    # Write all mappings at the end
    if mappings:
        write_location_mapping(mappings)
        write_perp_location_updates(mappings)
    
    # Process exceptions
    sequence = process_exception_mappings(existing, generated_locations, sequence)
    
    # Process NOT FOUND locations
    country_sequence = len(generated_countries) + 1
    country_sequence, state_sequence = process_not_found_locations(existing, generated_locations, generated_states, generated_countries, country_sequence, state_sequence)

if __name__ == "__main__":
    existing_records = load_existing_records()
    write_countries(existing_records)
    write_states(existing_records)
    write_locations(existing_records)
    print("Generated three SQL files: inserts_country.sql, inserts_state.sql, and inserts_location.sql and inserts_location_mapping.csv")

