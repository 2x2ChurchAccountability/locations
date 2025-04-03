import re

# Regular expression to standardize variations of "Glen Valley"
pattern_glen = re.compile(r'[Gg][Ll][Ee][Nn]\s*[Vv][Aa][Ll][Ll][Ee][Yy]\s*(\d+)')

# Pattern to match months that are followed by a space or dash, only at start of string
month_pattern = re.compile(r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b')
month_range_pattern = re.compile(r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*-\s*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b')
with_pattern = re.compile(r'(.*?)(?:with|With|w/|w/\s+)(.+)$')

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


def standardize_glen(text):
    return pattern_glen.sub(r'Glen Valley \1', text)

def extract_month(text):
    # Find all matches in the text
    matches = month_pattern.findall(text)
    return matches

def extract_month_range(text):
    # Find all matches in the text
    matches = month_range_pattern.findall(text)
    return matches

def extract_with(text):
    matches = with_pattern.findall(text)
    if matches:
        before, after = matches[0]  # Get the first match tuple
        return f"{before.strip()} With {' '.join(after.split())}"
    return None

def free_form_date_ranges(text):
    full_matches = []
    
    for match in date_range_pattern.finditer(text):
        first_month = match.group('first_month')
        first_day = match.group('first_day')
        second_month_with_day = match.group('second_month_with_day')
        second_month_only = match.group('second_month_only')
        second_day = match.group('second_day')
        
        print(f"\t\tfirst_month: {first_month}, first_day: {first_day}, second_month_with_day: {second_month_with_day}, second_month_only: {second_month_only}, second_day: {second_day}")
        
        if second_month_only:  # Month-to-month range without days
            full_match = f"{first_month} - {second_month_only}"
        elif not first_day:  # Just a month name
            full_match = first_month
        elif second_month_with_day and second_day:  # Month-to-month range with days
            full_match = f"{first_month} {first_day} - {second_month_with_day} {second_day}"
        elif second_day:  # Same month range
            full_match = f"{first_month} {first_day}-{second_day}"
        else:  # Single date
            full_match = f"{first_month} {first_day}"
        full_matches.append(full_match)
    
    return full_matches

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

# test_with_strings
test_with_strings = [
    "with Judy something",
    "With Judy something",
    "w/ Judy something",
    "w/Judy something",
    "New York with Judy something",
    "new york with Judy something",
    "new york w/ Judy something",
    "new york w/Judy something",
    "New York with Judy something and some more stuff",
    "new york with Judy something and some more stuff",
    "new york w/ Judy something and some more stuff",
    "new york w/Judy something and some more stuff"
]

# test_free_form_date_ranges_strings
test_free_form_date_ranges_strings = [
    "July 1-30",
    "July 1-August 30",
    "May 9-12",
    "Sept 5",
    "June 29-July2",
    "March",
    "Jun-Aug"
]

# test_get_month_or_range_strings
test_strings = [
    "Jul",
    'Jul-Aug',
    'Jan-Jun',
    'Jul-Dec',
    'Autumn',
    'Winter-Spring',
]

# Test the regex
for string in test_strings:
    print(f"Original: {string}")
    
    print(f"get_month_or_range: {get_month_or_range(string)}")
    
    # print(f"\tRaw matches: {date_range_pattern.findall(string)}")
    # print(f"date pattern: {free_form_date_ranges(string)}")
    
    # print(f"Standardized: {standardize_glen(string)}\n")

    # print(f"Extracted months: {extract_month(string)}")
    # print(f"Extracted month ranges: {extract_month_range(string)}\n")

    # print(f"With pattern: {extract_with(string)}")


    # with single_month_pattern, I only want to pick up the month if it is followed by a space.  If it's part of a word, like Nova or Juniper, I don't want to pick them up even though Nov and Jun are the first 3 characters.
    # with single_month_pattern, I only want to pick up the month if it is followed by a space.  If it's part of a word, like Nova or Juniper, I don't want to pick them up even though Nov and Jun are the first 3 characters.