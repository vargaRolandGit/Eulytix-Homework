import requests
from bs4 import BeautifulSoup
import pandas as pd

def make_senators(senators_data):
    senators = []
    i = 0
    while i < len(senators_data):
        # handle the case of multi-part names like "Van Hollen"
        if senators_data[i + 2] in ['Yea', 'Nay', 'Not']:
            name = senators_data[i]
            affiliation = senators_data[i + 1]
            state = affiliation[-3:-1] 
            affiliation = affiliation.split('-')[0][1]
            if senators_data[i + 2] == 'Not' and i + 3 < len(senators_data) and senators_data[i + 3] == 'Voting':
                record = 'Not Voting'
                i += 4  # Skip the extra word
            else:
                record = senators_data[i + 2]
                i += 3
        else:
            # handle two-part names
            name = f"{senators_data[i]} {senators_data[i + 1]}"
            affiliation = senators_data[i + 2]
            state = affiliation[-3:-1]
            affiliation = affiliation.split('-')[0][1]
            if senators_data[i + 3] == 'Not' and i + 4 < len(senators_data) and senators_data[i + 4] == 'Voting':
                record = 'Not Voting'
                i += 5  # skip the extra word
            else:
                record = senators_data[i + 3]
                i += 4

        senators.append(make_senator(name, record, affiliation, state))
        
    return senators

def make_vote_data(date, result, m_number, m_title, senators):
    return {
        'date': date,
        'result': result,
        'mesure_number': m_number,
        'measure_title': m_title,
        'senators': senators,
    } 

def make_senator(name, record, affiliation, state):
    return {
        'name' : name,
        'vote_record': record,
        'party_affiliation' : affiliation,
        'state' : state
    }


def fetch_site(vote_number):
    URL = f'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1182/vote_118_2_{str(vote_number).zfill(5)}.htm'
    html = requests.get(URL).text
    client = BeautifulSoup(html, 'lxml')

    title = client.find('h1').text
    blocks = client.find_all('div', class_ = 'contenttext')
    vote_info = blocks[0].find_all('div')
    senators_block = client.find('div', class_ = 'newspaperDisplay_3column')

    # list of strings (not BeautifulSoup element)
    senators_data = senators_block.text.replace('\n', ' ').replace(', ', ' ').split()
    result : str
    date : str

    for value in vote_info: 
        text_content = value.get_text(strip=True).split(':')
        for text in text_content:
            match text:
                case 'Vote Date': date = ''.join(text_content[1].split(',')[0:2])
                case 'Vote Result': result = text_content[1]


    return make_vote_data(date, result, vote_number, title, make_senators(senators_data))

def save_to_csv(output_name):
    data_list = []

    for i in range(255, 0, -1):
        vote_data = fetch_site(i)
        if vote_data and 'senators' in vote_data:
            data_list.append(vote_data)

    # flatten the data into a format suitable for CSV
    rows = []
    for vote in data_list:
        for senator in vote['senators']:
            row = {
                'date': vote['date'],
                'result': vote['result'],
                'measure_number': vote['mesure_number'],
                'measure_title': vote['measure_title'],
                'senator_name': senator['name'],
                'vote_record': senator['vote_record'],
                'party_affiliation': senator['party_affiliation'],
                'state': senator['state']
            }
            rows.append(row)

    df_votes = pd.DataFrame(rows)
    df_votes.to_csv(f'{output_name}.csv', index=False)


if __name__ == "__main__":
    save_to_csv('dataset')
    print('dataset saved')