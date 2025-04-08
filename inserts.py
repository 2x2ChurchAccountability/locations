import countries_data
import uuid
import os
import csv

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
        'locations': {}
    }
    
    # Load countries
    with open('curr_countries.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up the column names by removing quotes and BOM
            clean_row = {k.strip('"').strip('\ufeff'): v.strip('"') for k, v in row.items()}
            existing['countries'][clean_row['name']] = clean_row['recid']
    
    # Load states
    with open('curr_states.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up the column names by removing quotes and BOM
            clean_row = {k.strip('"').strip('\ufeff'): v.strip('"') for k, v in row.items()}
            key = (clean_row['country_recid'], clean_row['name'])
            existing['states'][key] = clean_row['recid']
    
    # Load locations
    with open('curr_locations.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up the column names by removing quotes and BOM
            clean_row = {k.strip('"').strip('\ufeff'): v.strip('"') for k, v in row.items()}
            key = (clean_row['state_recid'], clean_row['name'])
            existing['locations'][key] = clean_row['recid']
    
    return existing

def write_countries(existing):
    """Generate and write country insert statements."""
    sequence = 1
    with open('inserts_country.sql', 'w') as f:
        # First write all existing countries from CSV as comments
        for country_name, recid in existing['countries'].items():
            escaped_name = escape_single_quotes(country_name)
            f.write(f"-- INSERT INTO public.country (recid, name) VALUES ('{recid}', '{escaped_name}');\n")
        
        # Then handle countries from countries_data
        for country_name in countries_data.countries:
            escaped_name = escape_single_quotes(country_name)
            
            # Skip if country already exists (we already wrote it as a comment)
            if country_name in existing['countries']:
                continue
            
            # Generate new country
            recid = generate_guid('cccc', sequence)
            f.write(f"INSERT INTO public.country (recid, name) VALUES ('{recid}', '{escaped_name}');\n")
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
            f.write(f"-- INSERT INTO public.state (recid, country_recid, name) VALUES ('{state_recid}', '{country_recid}', '{escaped_name}');\n")
        
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
                
                if country_name == 'United States' and state_name == 'Colorado/Utah':
                    print(f"Generating state key in write_states: {key}")
                
                # Skip if state already exists (we already wrote it as a comment)
                if key in existing['states']:
                    continue
                
                # Generate new state
                recid = generate_guid('dddd', sequence)
                f.write(f"INSERT INTO public.state (recid, country_recid, name) VALUES ('{recid}', '{country_recid}', '{escaped_name}');\n")
                # Store the state key in existing['states']
                existing['states'][key] = recid
                sequence += 1

def write_locations(existing):
    """Generate and write location insert statements."""
    sequence = 1
    with open('inserts_location.sql', 'w') as f:
        # First write all existing locations from CSV as comments
        for (state_recid, location_name), location_recid in existing['locations'].items():
            escaped_name = escape_single_quotes(location_name)
            f.write(f"-- INSERT INTO public.location (recid, location_recid, name) VALUES ('{location_recid}', '{state_recid}', '{escaped_name}');\n")
        
        # Then handle locations from countries_data
        for country_name, country_data in countries_data.countries.items():
            # Get the country's recid from existing or generate a new one
            country_recid = existing['countries'].get(country_name, 
                generate_guid('cccc', list(countries_data.countries.keys()).index(country_name) + 1))
            
            print(f"Country: {country_name}  country_recid: {country_recid}")
            
            for city_name, state_names in country_data['cities'].items():
                found=False
                if city_name == 'Provo, Vernal':
                    found=True
                    print(f"City: {city_name}")
                for state_name in state_names:
                    # Replace --No State-- with country name before any processing
                    if state_name == '--No State--':
                        state_name = country_name
                    
                    if found: print(f"State: {state_name}  City: {city_name}")
                    # Get the state's recid - use the state name directly from the mapping
                    state_key = (country_recid, state_name)
                    if found: print(f"state_key: {state_key}")
                    
                    # Get the state_recid from existing states
                    if state_key not in existing['states']:
                        print(f"WARNING: State {state_name} not found in existing states for country {country_name}")
                        continue
                        
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
                    recid = generate_guid('dddd', sequence)
                    f.write(f"INSERT INTO public.location (recid, state_recid, name) VALUES ('{recid}', '{state_recid}', '{escaped_name}');\n")
                    sequence += 1

if __name__ == "__main__":
    existing_records = load_existing_records()
    write_countries(existing_records)
    write_states(existing_records)
    write_locations(existing_records)
    print("Generated three SQL files: inserts_country.sql, inserts_state.sql, and inserts_location.sql")

