# locations - POC formatting the output of extract and putting out | delimited info to feed into location_import.

### Pull down the **locations** repo and install the needed components

```bash
git clone git@github.com:permitsaige/locations.git
cd locations
python3 -m venv locations_venv
source locations_venv/bin/activate
pip install -r requirements.txt
```

TODO: Create a .env.local file with supabase settings
```bash
echo -e "NEXT_PUBLIC_SUPABASE_URL=https://<yourSupabaseUrlPrevix>.supabase.co\n\
NEXT_PUBLIC_SUPABASE_ANON_KEY=<yourSupabaseAPIKey>\n\
NEXT_PUBLIC_DB_SCHEMA=public" > .env.local
```

TODO: From the above .env.local, the LOG_DIR states a directory that logs will be written to.  The way the logger is setup in process_locations.py, all logs will go to the console as well.

#### Running the location formatting POC

```bash
python process_locations.py
```
### How this POC works

There is a directory named inputs.  There are txt files in there were created by the extract project.

When the process runs, it reads the input files one at a time determines what to process and format.  Each line output is formatted exactly the same and | delimited.

The output is to the console with the idea that the next step will be 

```bash
python process_locations.py | python location_import.py
```

## Notes for David

These are the pieces of code in here:

```
countries_data.py
cities.py
insert_csl.py
insert_perp_locations.py
process_locations.py

test_process_locations.py
test_process_locations_trial.py
```

Here's some info on what they handle
| File Name    | Input | Output | Notes |
| -------- | ------- |------- |------- |
|countries_data.py|||This is used to understand countries, their states and their locations.  Used primarily by process_locations.py|
|cities.py|reads in wl.txt|outputs content for a new countries_data.py|I am thinking this should never be used again.  If something like this is needed, I believe it will need to be rewritten to accomidate how things stand at that point in time|
|insert_csl.py|curr_countries.csv, curr_states.csv, curr_locations.csv which are outputs of the exising tables|inserts_country.sql, inserts_state.sql, inserts_location.sql and inserts_perp_location.py|processes data in countries_data.py considering the current info from the csv's and build inserts to the country, state and location tables.  Additionally some update statements to perp_location to adjust existing location_recid's|
|insert_perp_locations.py|output from process_locations.py piped in|by default, insert commands to the console, but can insert directly to the perp_location table.  If needed, also builds a process_location.sql and process_state.sql files|There is an --insert option that I haven't used".  If process_location.sql and/or process_state.sql contain insert statements, they must be executed before the perp_location inserts can be successfully executed.  There is a --debug option that turns on a lot debug/information output|
|process_locations.py|By default, processes all of the files in the inputs directory.  Optionally a --file switch can be used to read a single file in the inputs directory |To the console, pipe delimited lines containing info to be used to insert perp_location records|THIS IS THE BIG DOG, EVERYTHING ELSE WAS BUILT IN SUPPORT OF THIS.  There is a --validate switch that turns on a lot of additional output.  This switch is also turned on when the unit tests are running|
|test_process_locations.py||Unit Test Success/Failure|These are the unit tests that MUST be run any time you change anything in process_locations.py|
|test_process_locations_trial.py||Unit Test Success/Failure|Unit Test that I am working on.  Just used for one or two so I can isolate|

## How I run things

### The final processing
```bash
python process_locations.py > abc2.txt
cat abc2.txt | python insert_perp_locations.py > xx.txt 2> xx2.txt
# Check to see if there are insert statements in process_state.sql or process_locatoin.sql and if so, insert using SQL Editor
# Once any state and/or location records have been inserted, you can continue with inserting the perp_location records

# Then use the insert statements in xx.txt and use the SQL Editor to execute them
# OR
cat abc2.txt | python insert_perp_locations.py --insert
```

### Building Country, State and Location records
```bash
python insert_csl.py
# Then use the SQL Editor to execute the contents of the three sql files
```