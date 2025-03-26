"""Data structure containing country information including states, variations, and cities."""

countries = {
    'United States': {
        'name': 'United States',
        'states': [
            'Oregon/South Idaho', 'Oregon/Southern Idaho', 'Montana/North Wyoming', 'New York/New England', 'Ohio/West Virginia',
            'Pennsylvania/Ohio/West Virginia', 'PA/NY/New England/NJ/OH', 'PA/NY/New England/NJ',
            'Kentucky/Tennessee', 'Tennessee/Kentucky', 'Montana/Wyoming', 'Alabama/Mississippi', 'Kansas/Nebraska',
            'Maryland/Delaware', 'Colorado/Utah',
            'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'Chino California', 'California', 'Colorado', 'Connecticut', 
            'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 
            'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 
            'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 
            'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 
            'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 
            'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 
            'Wisconsin', 'Wyoming'
        ],
        'state_variations': {
            'New Dakota': 'North Dakota',
            'Virgina': 'Virginia',
            'Washing': 'Washington',
            'Kanasa': 'Kansas',
            'AL': 'Alabama',
            'AK': 'Alaska',
            'AZ': 'Arizona',
            'AR': 'Arkansas',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'HI': 'Hawaii',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'IA': 'Iowa',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'ME': 'Maine',
            'MD': 'Maryland',
            'MA': 'Massachusetts',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MS': 'Mississippi',
            'MO': 'Missouri',
            'MT': 'Montana',
            'NE': 'Nebraska',
            'NV': 'Nevada',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NY': 'New York',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VT': 'Vermont',
            'VA': 'Virginia',
            'WA': 'Washington',
            'WV': 'West Virginia',
            'WI': 'Wisconsin',
            'WY': 'Wyoming'
        },
        'cities': {
            'Picton': 'Oklahoma',
            'Anadarko': 'Oklahoma',
            'Buttonwillow': 'California',
            'Eagle Bend': 'Minnesota',
            'Eagle Bend 1': 'Minnesota',
            'Buttonwillow 2': 'California',
            'Knoxville': 'Tennessee',
            'Gilbert': 'Arizona',
            'Anchorage': 'Alaska',
            'Clover': 'South Carolina',
            'Alma': 'Michigan'
        }
    },
    'Canada': {
        'name': 'Canada',
        'states': [
            'Quebec and Atlantic', 'Ontario/Quebec',
            'Manitoba/Northwest Ontario', 'Manitoba/Ontario', 'Saskatchewan/Manitoba/Northwest Ontario', 
            'Saskatchewan/Manitoba', 'Quebec/Atlantic', 'Calgary', 'Maritimes',
            'Alberta', 'Atlantic', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador',
            'Nova Scotia', 'Ontario', 'Prince Edward Island', 'Quebec', 'Saskatchewan',
            'Northwest Territories', 'Nunavut', 'Yukon'
        ],
        'state_variations': {
            'SK': 'Saskatchewan',
            'BC': 'British Columbia',
            'AB': 'Alberta',
            'MB': 'Manitoba',
            'ON': 'Ontario',
            'QC': 'Quebec',
            'NB': 'New Brunswick',
            'NS': 'Nova Scotia',
            'PE': 'Prince Edward Island',
            'NL': 'Newfoundland and Labrador',
            'Newfoundland': 'Newfoundland and Labrador',
            'NT': 'Northwest Territories',
            'NU': 'Nunavut',
            'YT': 'Yukon'
        },
        'cities': {
            'Salmon Arm': 'Saskatchewan',
            'Portage': 'Manitoba',
            'Prince George': 'British Columbia',
            'Irishtown': 'Newfoundland and Labrador',
            'Glen Valley 2': 'British Columbia',
            'Glen Valley': 'British Columbia'
        }
    },
    'Austria': {
        'name': 'Austria',
        'states': [],
        'cities': {}
    },
    'Germany': {
        'name': 'Germany',
        'states': [],
        'cities': {}
    },
    'Orient': {
        'name': 'Orient',
        'states': [],
        'special_location': 'Convention',
        'cities': {}
    },
    'Nigeria': {
        'name': 'Nigeria',
        'states': [],
        'cities': {}
    },
    'Belgium': {
        'name': 'Belgium',
        'states': [],
        'cities': {}
    },
    'Sri Lanka': {
        'name': 'Sri Lanka',
        'states': [],
        'special_location': 'Convention',
        'cities': {}
    },
    'Guam': {
        'name': 'Guam',
        'states': [],
        'special_location': 'Convention',
        'cities': {}
    },
    'Peru': {
        'name': 'Peru',
        'states': ['Olmos'],
        'special_location': 'Convention',
        'cities': {}
    },
    'Bolivia': {
        'name': 'Bolivia',
        'states': [],
        'special_location': 'Convention',
        'cities': {}
    },
    'Australia/Papua New Guinea': {
        'name': 'Australia/Papua New Guinea',
        'states': ['Tasmania'],
        'cities': {}
    },
    'Australia': {
        'name': 'Australia',
        'states': ['Victoria', 'Victoria and Tasmania', 'Tasmania', 'New South Wales', 'Queensland', 'South Australia', 'Western Australia', 'Northern Territory', 'Australian Capital Territory'],
        'variations': ['Australian'],
        'cities': {}
    },
    'New Zealand': {
        'name': 'New Zealand',
        'states': [],
        'cities': {}
    },
    'United Kingdom': {
        'name': 'United Kingdom',
        'variations': ['UK'],
        'states': [],
        'cities': {}
    },
    'Ireland': {
        'name': 'Ireland',
        'states': [],
        'cities': {}
    },
    'South Africa': {
        'name': 'South Africa',
        'variations': ['S. Africa'],
        'states': ['Johannesburg'],
        'cities': {}
    },
    'West Africa': {
        'name': 'West Africa',
        'variations': ['W. Africa'],
        'states': [],
        'cities': {}
    },
    'Africa': {
        'name': 'Africa',
        'states': [],
        'cities': {}
    },
    'South America': {
        'name': 'South America',
        'states': [],
        'cities': {}
    },
    'Finland': {
        'name': 'Finland',
        'states': [],
        'cities': {}
    },
    'Netherlands': {
        'name': 'Netherlands',
        'states': [],
        'cities': {}
    },
    'Jamaica': {
        'name': 'Jamaica',
        'states': [],
        'cities': {}
    },
    'Haiti': {
        'name': 'Haiti',
        'states': [],
        'cities': {}
    },
    'Korea': {
        'name': 'Korea',
        'states': [],
        'cities': {}
    },
    'Philippines': {
        'name': 'Philippines',
        'states': [],
        'cities': {}
    },
    'Argentina/Paraguay/Uruguay': {
        'name': 'Argentina/Paraguay/Uruguay',
        'states': [],
        'cities': {}
    },
    'Argentina/Paraguay': {
        'name': 'Argentina/Paraguay',
        'states': [],
        'cities': {}
    },
    'Brazil and Uruguay': {
        'name': 'Brazil and Uruguay',
        'states': [],
        'cities': {}
    },
    'Brazil': {
        'name': 'Brazil',
        'states': [],
        'cities': {}
    },
    'Ecuador': {
        'name': 'Ecuador',
        'states': ['La Paz', 'Galapagos'],
        'cities': {}
    },
    'India': {
        'name': 'India',
        'states': ['Bangalore'],
        'cities': {}
    },
    'Scotland': {
        'name': 'Scotland',
        'states': [],
        'cities': {}
    },
    'Trinidad': {
        'name': 'Trinidad',
        'states': [],
        'cities': {}
    },
    'Japan': {
        'name': 'Japan',
        'states': ['Tokyo'],
        'cities': {}
    },
    'Guatemala': {
        'name': 'Guatemala',
        'states': [],
        'cities': {}
    },
    'Denmark': {
        'name': 'Denmark',
        'states': [],
        'cities': {}
    },
    'Mexico': {
        'name': 'Mexico',
        'states': [],
        'cities': {}
    },
    'Spain': {
        'name': 'Spain',
        'states': [],
        'cities': {}
    },
    'Greece': {
        'name': 'Greece',
        'states': [],
        'cities': {}
    },
    'Argentina': {
        'name': 'Argentina',
        'states': [],
        'cities': {
            'Rio Cuarto': '',
            'San Rafael': '',
            'Cipolletti': ''
        }
    },
    'Italy': {
        'name': 'Italy',
        'states': [],
        'cities': {}
    },
    'France': {
        'name': 'France',
        'states': ['Paris'],
        'cities': {}
    },
    'Romania': {
        'name': 'Romania',
        'states': [],
        'cities': {}
    },
    'Sweden': {
        'name': 'Sweden',
        'states': ['Stockholm'],
        'cities': {}
    },
    'Norway': {
        'name': 'Norway',
        'states': [],
        'cities': {}
    },
    'Venezuela': {
        'name': 'Venezuela',
        'states': ['Caracas', 'Barquisimeto'],
        'cities': {}
    },
    'Taiwan': {
        'name': 'Taiwan',
        'states': [],
        'cities': {}
    },
    'Poland': {
        'name': 'Poland',
        'states': [],
        'cities': {}
    },
    'Columbia': {
        'name': 'Columbia',
        'variations': ['Colombia'],
        'states': ['Ipiales'],
        'cities': {}
    },
    'Grand Cayman': {
        'name': 'Grand Cayman',
        'states': [],
        'cities': {}
    },
    'Barbados': {
        'name': 'Barbados',
        'states': [],
        'cities': {}
    },
    'Guyana': {
        'name': 'Guyana',
        'states': [],
        'cities': {}
    },
    'Hong Kong': {
        'name': 'Hong Kong',
        'states': [],
        'cities': {}
    },
    'China': {
        'name': 'China',
        'states': [],
        'cities': {}
    },
    'Saipan': {
        'name': 'Saipan',
        'states': [],
        'cities': {}
    },
    'Dominican Republic': {
        'name': 'Dominican Republic',
        'variations': ['Republica Dominicana'],
        'states': [],
        'cities': {}
    },
    'Suriname': {
        'name': 'Suriname',
        'states': [],
        'cities': {}
    },
    'Nevis': {
        'name': 'Nevis',
        'states': [],
        'cities': {}
    },
    'St. Kitts': {
        'name': 'St. Kitts',
        'states': [],
        'cities': {}
    },
    'Antigua': {
        'name': 'Antigua',
        'states': [],
        'cities': {}
    },
    'Caribbean': {
        'name': 'Caribbean',
        'states': ['Antigua', 'Barbados', 'Cayman Islands', 'Dominican Republic', 'Grenada', 'Guadeloupe', 'Haiti', 'Jamaica', 'St. Kitts', 'St. Lucia', 'St. Vincent', 'Trinidad'],
        'cities': {}
    },
    'Cayman Islands': {
        'name': 'Cayman Islands',
        'states': [],
        'variations': ['Cayman Brac'],
        'cities': {}
    },
    'Zimbabwe': {
        'name': 'Zimbabwe',
        'states': ['Serial'],
        'cities': {}
    },
    'Pakistan': {
        'name': 'Pakistan',
        'states': ['Mirpur Khas'],
        'cities': {}
    }
} 