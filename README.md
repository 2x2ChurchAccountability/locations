# locations - POC formatting the output of extract and putting out | delimited info to feed into location_import.

### Pull down the **locations** repo and install the needed components

```bash
git clone git@github.com:permitsaige/locations.git
cd locations
python3 -m venv locations_venv
source locations_venv/bin/activate
pip install -r requirements.txt
```

TODO: Create a .env.local file with logging settings
```bash
echo -e "LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL\n\
LOG_FORMAT=%(asctime)s - %(levelname)s - %(message)s\n\
LOG_DIR=logs" > .env.local
```
TODO: From the above .env.local, the LOG_DIR states a directory that logs will be written to.  The way the logger is setup in process_locations.py, all logs will go to the console as well.

#### Running the location formatting POC

```bash
python src/process_locations.py
```
### How this POC works

There is a directory named inputs.  There are txt files in there were created by the extract project.

When the process runs, it reads the input files one at a time determines what to process and format.  Each line output is formatted exactly the same and | delimited.

The output is to the console with the idea that the next step will be 

```bash
python process_locations.py | python location_import.py
```
