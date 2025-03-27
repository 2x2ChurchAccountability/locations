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
            'Eagle Bend 1': 'Minnesota',
            'Eagle Bend 2': 'Minnesota',
            'Eagle Bend': 'Minnesota',
            'Buttonwillow 1': 'California',
            'Buttonwillow 2': 'California',
            'Buttonwillow': 'California',
            'Knoxville': 'Tennessee',
            'Gilbert': 'Arizona',
            'Anchorage': 'Alaska',
            'Clover': 'South Carolina',
            'Alma': 'Michigan',
            'Albuquerque': 'New Mexico',
            'Altamont': 'New York',
            'Apopka': 'Florida',
            'Bakersfield': 'California',
            'Bird City': 'Kansas',
            'Black Hills': 'South Dakota',
            'Blackwater': 'Missouri',
            'Bonners Ferry': 'Idaho',
            'Boring 1': 'Oregon',
            'Boring 2': 'Oregon',
            'Boring': 'Oregon',
            'Boston': 'Virginia',
            'Boyden': 'Iowa',
            'Bradley': 'Oklahoma',
            'Brownstown': 'Illinois',
            'Bushnell': 'Florida',
            'Cando': 'North Dakota',
            'Carsonville': 'Michigan',
            'Casa Grande 1': 'Arizona',
            'Casa Grande 2': 'Arizona',
            'Casa Grande': 'Arizona',
            'Cassatt': 'South Carolina',
            'Chelan': 'Washington',
            'Chugwater': 'Wyoming',
            'Clever': 'Missouri',
            'Clyde': 'Ohio',
            'Cody': 'Wyoming',
            'Dagmar': 'Montana',
            'Dells': 'Wisconsin',
            'Demorest': 'Georgia',
            'Denton': 'North Carolina',
            'Devon': 'Montana',
            'Downings': 'Virginia',
            'Eaton': 'Ohio',
            'Edgewood': 'New Mexico',
            'Effie': 'Louisiana',
            'Elizabeth 1': 'Colorado',
            'Elizabeth 2': 'Colorado',
            'Elizabeth': 'Colorado',
            'Fosters': 'Alabama',
            'Fosters': 'Alabama',
            'Freedom': 'New York',
            'Gastonia': 'North Carolina',
            'Georgetown': 'Texas',
            'Gilroy #1': 'California',
            'Gilroy': 'California',
            'Happy': 'Texas',
            'Hector': 'Minnesota',
            'Hermosa': 'South Dakota',
            'Hotchkiss': 'Colorado',
            'Hunter': 'North Dakota',
            'Jackson': 'Mississippi',
            'Juneau': 'Alaska',
            'Lexington': 'Kentucky',
            'lltown 1 Washington': 'Michigan',
            'Madisonville': 'Kentucky',
            'Malcom': 'Iowa',
            'Mandan': 'North Dakota',
            'Manhattan 2': 'Montana',
            'Manhattan': 'Montana',
            'Marion': 'Wisconsin',
            'Marysville': 'Kansas',
            'May Mountain Ranch': 'California',
            'McCordsville': 'Indiana',
            'Menomonie': 'Wisconsin',
            'Metter': 'Georgia',
            'Milford': 'New Hampshire', 
            'Milltown 1': 'Washington',
            'Milltown 2': 'Washington',
            'Milltown': 'Washington',
            'Mountain Peak': 'Texas',
            'Mountain Ranch 1': 'California',
            'Mountain Ranch 2': 'California',
            'Mountain Ranch': 'California',
            'Mountainair 1': 'New Mexico',
            'Mountainair 2': 'New Mexico',
            'Mountainair': 'New Mexico',
            'Mt. Peak': 'Texas',
            'Mt. Sterling': 'Illinois',
            'Newry': 'Pennsylvania',
            'Olympia 1': 'Washington',
            'Olympia 2': 'Washington',
            'Olympia': 'Washington',
            'Orick': 'California',
            'Parma': 'Idaho',
            'Paris': 'Tennessee',
            'Perry': 'Oklahoma',
            'Post Falls': 'Idaho',
            'Pulaski': 'Virginia',
            'Quakertown': 'Pennsylvania',
            'Riverton': 'Utah',
            'Rogers': 'Arkansas',
            'Ronan': 'Montana',
            'Saginaw 1': 'Oregon',
            'Saginaw 2': 'Oregon',
            'Saginaw': 'Oregon',
            'Salvisa': 'Kentucky',
            'Santee': 'California',
            'Seneca': 'Illinois',
            'Sharon': 'Ohio',
            'Shelby': 'North Carolina',
            'Shelter Valley': 'California',
            'Shoals': 'Indiana',
            'Texarkana': 'Texas',
            'Utica 2': 'South Dakota',
            'Utica': 'South Dakota',
            'Vanderbilt': 'Michigan',
            'Walla Walla': 'Washington',
            'Wasilla': 'Alaska',
            'Yellow Springs': 'Ohio',
            'York': 'Nebraska'
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
            'Almonte': '',
            'Antler': 'Saskatchewan',
            'Aylesbury': 'Saskatchewan',
            'Bowsman': '',
            'Brigus': '',
            'Didsbury': 'Alberta',
            'Didsbury #2': 'Alberta',
            'Didsbury 1': 'Alberta',
            'Didsbury 2': 'Alberta',
            'Didsbury 2': 'Alberta',
            'Duncan': 'British Columbia',
            'Dunnville': '',
            'Ellershouse': '',
            'Emo': '',
            'Freedom': '',
            'Freetown': 'Prince Edward Island',
            'Freetown I': 'Prince Edward Island',
            'Glen Valley 1': 'British Columbia',
            'Glen Valley 2': 'British Columbia',
            'Glen Valley': 'British Columbia',
            'Greenshield': '',
            'Harvey Station': '',
            'Humber Village': 'Newfoundland and Labrador',
            'Hythe': '',
            'Irishtown': 'Newfoundland and Labrador',
            'Iron Bridge': 'Ontario',
            'Mellowdale': '',
            'Napan': '',
            'Portage': 'Manitoba',
            'Prince George': 'British Columbia',
            'Richmond': '',
            'Salmon Arm': 'Saskatchewan',
            'Seagrave': '',
            'Silverdale 1': '',
            'Silverdale 2': '',
            'Smeaton': '',
            'St. George': 'Newfoundland and Labrador',
            'Strathroy': '',
            'Theodore': 'Saskatchewan',
            'Woodstock': ''
        }
    },
    'Austria': {
        'name': 'Austria',
        'states': [],
        'cities': {
            'Vienna': ''
        }
    },
    'Germany': {
        'name': 'Germany',
        'states': [],
        'cities': {
            'Hulben': ''
        }
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
        'cities': {
            'Ikorodu': ''
        }
    },
    'Belgium': {
        'name': 'Belgium',
        'states': [],
        'cities': {
            'Lillois': '',
            'Sart-Dames-Avelines': ''
        }
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
        'states': ['Lambayeque'],
        'special_location': 'Convention',
        'cities': {
            'Olmos': 'Lambayeque',
            'Coyunde': ''
        }
    },
    'Bolivia': {
        'name': 'Bolivia',
        'states': ['La Paz'],
        'special_location': 'Convention',
        'cities': {
            'Cochabamba': ''
        }
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
        'cities': {
            'Biddeston': '',
            'Chelona 2': '',
            'Colac': 'Victoria',
            'Drouin': 'Victoria',
            'Glenco': '',
            'Kapunda 1': '',
            'Kapunda 2': '',
            'Maroota 1': '',
            'Maroota 2': '',
            'Mudgee': 'New South Wales',
            'Pilerwa #1': '',
            'Pilerwa #2': '',
            'Pilerwa 1': '',
            'Rochedale': '',
            'Speed': 'Victoria',
            'Thoona': 'Victoria',
            'Watta': 'New South Wales',
            'Williams': '',
            'Williams 1': '',
            'Williams 2': '',
            'Wilmington': ''
        }
    },
    'New Zealand': {
        'name': 'New Zealand',
        'states': [],
        'cities': {
            'Masterton 1': '',
            'Masterton': '',
            'Ngaere': '',
            'Pukekone 2': '',
            'Pukekohe': '',
            'Winchester 1': ''
        }
    },
    'United Kingdom': {
        'name': 'United Kingdom',
        'variations': ['UK'],
        'states': [],
        'cities': {
            'Dunbarton 1': '',
            'Gloucester 2': '',
            'Lancashire': '',
            'Yorkley 2': ''
        }
    },
    'Ireland': {
        'name': 'Ireland',
        'states': [],
        'cities': {
            'Carrick': '',
            'Down': '',
            'Fermanagh': '',
            'Laois': '',
            'Monaghan': ''
        }
    },
    'South Africa': {
        'name': 'South Africa',
        'variations': ['S. Africa'],
        'states': ['Johannesburg'],
        'cities': {
            'Bloemfontein': '',
            'Cape 1': '',
            'Cape 2': '',
            'Cape Town': '',
            'Durban': '',
            'Gbetagbo': '',
            'Port Elizabeth': '',
            'Pretoria 1': '',
            'Pretoria 2': '',
            'Pretoria': ''
        }
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
        'cities': {
            'Vaasa': ''
        }
    },
    'Netherlands': {
        'name': 'Netherlands',
        'states': [],
        'cities': {
            'Putten': ''
        }
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
        'cities': {
            'Puchon': '',
            'Seoul South': ''
        }
    },
    'Philippines': {
        'name': 'Philippines',
        'states': [],
        'cities': {
            'Baguio': '',
            'Cavite': '',
            'Iloilo': '',
            'Ilocos': '',
            'Ozamis': '',
            'Rosales': ''
        }
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
        'cities': {
            'Alegrete': '',
            'Bel Horizonte': '',
            'Gravati': '',
            'Gravati': '',
            'Panambi': '',
            'Sao Jose dos Campos': '',
            'Sao Paulo': ''
        }
    },
    'Ecuador': {
        'name': 'Ecuador',
        'states': ['Galapagos'],
        'cities': {
            'El Cristal': ''
        }
    },
    'India': {
        'name': 'India',
        'states': [],
        'cities': {'Bangalore': ''}
    },
    'Scotland': {
        'name': 'Scotland',
        'states': [],
        'cities': {
            'Gartocharn 1': '',
            'Gartocharn 2': ''
        }
    },
    'Trinidad': {
        'name': 'Trinidad',
        'states': [],
        'cities': {}
    },
    'Japan': {
        'name': 'Japan',
        'states': [],
        'cities': {'Tokyo': ''}
    },
    'Guatemala': {
        'name': 'Guatemala',
        'states': [],
        'cities': {
            'Malacation': ''
        }
    },
    'Denmark': {
        'name': 'Denmark',
        'states': [],
        'cities': {
            'Sonder Omme': ''
        }
    },
    'Mexico': {
        'name': 'Mexico',
        'states': [],
        'cities': {
            'Ebano': '',
            'Insurgentes': '',
            'Tanama': ''
        }
    },
    'Spain': {
        'name': 'Spain',
        'states': [],
        'cities': {
            'Madrid': ''
        }
    },
    'Greece': {
        'name': 'Greece',
        'states': [],
        'cities': {
            'Athens': '',
            'Inoi': ''
        }
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
        'cities': {
            'Petacciato': ''
        }
    },
    'France': {
        'name': 'France',
        'states': [],
        'cities': {
            'Ales': '',
            'Chaintreauville': '',
            'Chaintreauville': '',
            'Chaintreauville': '',
            'Chaintreauville': '',
            'Foljuif': '',
            'Foljuif': '',
            'Paris': ''
        }
    },
    'Romania': {
        'name': 'Romania',
        'states': [],
        'cities': {
            'Sibiu 2': ''
        }
    },
    'Sweden': {
        'name': 'Sweden',
        'states': ['Stockholm'],
        'cities': {}
    },
    'Norway': {
        'name': 'Norway',
        'states': [],
        'cities': {
            'Stokke': ''
        }
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
        'cities': {
            'Wista': ''
        }
    },
    'Columbia': {
        'name': 'Columbia',
        'variations': ['Colombia'],
        'states': ['Ipiales'],
        'cities': {
            'Bogota': ''
        }
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
    'China': {
        'name': 'China',
        'states': [],
        'cities': {
            'Hong Kong': ''
        }
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
        'cities': {
            'Bonao': ''
        }
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
        'cities': {
            'Cabaret': 'Haiti'
        }
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