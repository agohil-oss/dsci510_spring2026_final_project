#don't need to upload results in that folder, he will do it himself
#all sources and intermediate datasets will be in data folder
#need .env and .env.example - look into
#_________________
#NOAA Climate Data
#_________________

#Reading the State-Level data
import urllib.request
import sqlite3
import csv
import os
import re
from config import DATA_DIR, DB_PATH, NOAA_BASE_URL, USDA_CSV

#Wrote function that uses regex to retrieve latest NOAA data since updates monthly
def get_noaa_date_stamp():
    print("Checking NOAA directory for latest files...")
    with urllib.request.urlopen(NOAA_BASE_URL) as response:
        html = response.read().decode('utf-8')
    match = re.search(r'climdiv-tmaxst-v1\.0\.0-(\d{8})', html)
    if not match:
        raise RuntimeError("Could not find current NOAA date stamp.")
    date_stamp = match.group(1)
    print(f"Latest NOAA date stamp: {date_stamp}")
    return date_stamp

def download_noaa_files(date_stamp, output_dir):
    files = [
        f"{NOAA_BASE_URL}climdiv-tmaxst-v1.0.0-{date_stamp}",
        f"{NOAA_BASE_URL}climdiv-tminst-v1.0.0-{date_stamp}",
        f"{NOAA_BASE_URL}climdiv-tmpcst-v1.0.0-{date_stamp}",
        f"{NOAA_BASE_URL}climdiv-pcpnst-v1.0.0-{date_stamp}",
    ]
    for f in files:
        filename    = f.split("/")[-1]
        output_path = os.path.join(output_dir, filename)
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(f, output_path)
        print(f"Saved → {output_path}")
    return date_stamp

#Creating Crop Yield Table
def create_tables(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS crop_yield (
            state TEXT,
            year INTEGER,
            commodity TEXT,
            yield REAL, 
            PRIMARY KEY (state, year, commodity)
            )
    ''')

    #Creating Climate Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS climate (
            state TEXT, 
            state_code TEXT,
            year INTEGER,
            month TEXT, 
            tmax REAL, 
            tmin REAL,
            tavg REAL,
            precip REAL,
            PRIMARY KEY (state_code, year, month)
        )  
    ''')
    print("Tables created")

#Data Cleaning for USDA Data
def load_usda_data(cur, output_dir):
    print("Loading USDA crop yield data..")

    USDA_loaded = 0
    USDA_skipped = 0

    USDA_path = os.path.join(output_dir, USDA_CSV)

    with open(USDA_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row['Period'].strip().upper() != "YEAR":
                USDA_skipped += 1                              #skips rows that don't have yearly data
                continue

            if row['Value'].strip() == '':
                USDA_skipped += 1                              #skip rows with missing yield values
                continue

            state = row['State'].strip().title()
            year = int(row['Year'].strip())
            commodity = row['Commodity'].strip().title()
            yield_val = float(row['Value'].replace(',', ''))

            cur.execute('''
                INSERT OR IGNORE INTO crop_yield (state, year, commodity, yield)
                VALUES (?, ?, ?, ?)
            ''', (state, year, commodity, yield_val))
            USDA_loaded += 1

    print(f"USDA data transformation complete: {USDA_loaded} valid rows and {USDA_skipped} skipped rows")


#Refining NOAA climate data

def load_noaa_data(cur, date_stamp, OUTPUT_DIR):
    # Detail Data by State and Region

    states = {
        '01': 'Alabama',
        '02': 'Arizona',
        '03': 'Arkansas',
        '04': 'California',
        '05': 'Colorado',
        '06': 'Connecticut',
        '07': 'Delaware',
        '08': 'Florida',
        '09': 'Georgia',
        '10': 'Idaho',
        '11': 'Illinois',
        '12': 'Indiana',
        '13': 'Iowa',
        '14': 'Kansas',
        '15': 'Kentucky',
        '16': 'Louisiana',
        '17': 'Maine',
        '18': 'Maryland',
        '19': 'Massachusetts',
        '20': 'Michigan',
        '21': 'Minnesota',
        '22': 'Mississippi',
        '23': 'Missouri',
        '24': 'Montana',
        '25': 'Nebraska',
        '26': 'Nevada',
        '27': 'New Hampshire',
        '28': 'New Jersey',
        '29': 'New Mexico',
        '30': 'New York',
        '31': 'North Carolina',
        '32': 'North Dakota',
        '33': 'Ohio',
        '34': 'Oklahoma',
        '35': 'Oregon',
        '36': 'Pennsylvania',
        '37': 'Rhode Island',
        '38': 'South Carolina',
        '39': 'South Dakota',
        '40': 'Tennessee',
        '41': 'Texas',
        '42': 'Utah',
        '43': 'Vermont',
        '44': 'Virginia',
        '45': 'Washington',
        '46': 'West Virginia',
        '47': 'Wisconsin',
        '48': 'Wyoming',
        '49': 'Hawaii',
        '50': 'Alaska',

        '101': 'Northeast Region',
        '102': 'East North Central Region',
        '103': 'Central Region',
        '104': 'Southeast Region',
        '105': 'West North Central Region',
        '106': 'South Region',
        '107': 'Southwest Region',
        '108': 'Northwest Region',
        '109': 'West Region',
        '110': 'National (contiguous 48 States)'
    }

    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV",
              "DEC"]  # holding the months in a list to call back to dictionary

    print("Now sifting through NOAA data files...")

    data_fields = {
        f"climdiv-tmaxst-v1.0.0-{date_stamp}": "tmax",
        f"climdiv-tminst-v1.0.0-{date_stamp}": "tmin",
        f"climdiv-tmpcst-v1.0.0-{date_stamp}": "tavg",
        f"climdiv-pcpnst-v1.0.0-{date_stamp}": "precip",
    }

    NOAAclimate_data = {}                     #going to populate clean data into this dictionary

    for filename, field in data_fields.items():
        fpath = os.path.join(OUTPUT_DIR, filename)
        with open(fpath, 'r') as f:
            for line in f:
                parts = line.split()

                if len(parts) < 13:
                    continue

                code = parts[0]
                state_code = code[:2]
                year = int(code[6:10])    #check if this is the right slicing?
                values = parts[1:13]

                if state_code not in states:   #skip all data that doesn't have state data
                    continue

                for i,val in enumerate(values):
                    key = (state_code, year, months[i])

                    #start storing data from scratch
                    if key not in NOAAclimate_data:
                        NOAAclimate_data[key] = {
                            'state': states[state_code],
                            'state_code': state_code,
                            'year': year,
                            'month': months[i],
                            'tmax': None,
                            'tmin': None,
                            'tavg': None,
                            'precip': None,
                        }

                    flo_val = float(val)

                    #NOAA data cleaning, skip all invalid rows
                    if flo_val == -99.99:
                        continue
                    if field in ('tmax', 'tavg') and not (-60 < flo_val < 150):
                        continue
                    if field == 'tmin' and not (-80 < flo_val < 120):
                        continue
                    if field == 'precip' and flo_val < 0:
                        continue

                    NOAAclimate_data[key][field] = flo_val


    # Inserting Climate Data into SQL shell
    NOAA_loaded = 0
    NOAA_skipped = 0

    for row in NOAAclimate_data.values():
        if None in (row['tmax'], row['tmin'], row['tavg'], row['precip']):       #skips the missing values in the dataset
            NOAA_skipped += 1
            continue

        cur.execute('''
            INSERT OR IGNORE INTO climate 
                (state, state_code, year, month, tmax, tmin, tavg, precip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['state'],
            row['state_code'],
            row['year'],
            row['month'],
            row['tmax'],
            row['tmin'],
            row['tavg'],
            row['precip']
        ))
        NOAA_loaded += 1

def build_database():
    os.makedirs(DATA_DIR, exist_ok=True)

    date_stamp = get_noaa_date_stamp()
    download_noaa_files(date_stamp, DATA_DIR)

    db_path = os.path.join(DATA_DIR, 'agclimate.db')
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    create_tables(cur)
    load_usda_data(cur, DATA_DIR)
    load_noaa_data(cur, date_stamp, DATA_DIR)

    conn.commit()
    conn.close()

    print(f"Agclimate.db loaded {DB_PATH}")








