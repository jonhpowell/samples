import requests
import csv
import json
import copy


class CoinMarketCapReader(Exception):

    '''
        Read Cryptocoin API for recent day's data (JSON) & save to a csv file.

        To improve:
            1) Make error handling more bullet-proof
            2) Use gcloud commands to upload csv to GCP cloud storage
    '''
    def read_market_cap_api(self, uri):

        try:
            c_res = requests.get(uri)
#            print c_res, c_res.text
            if c_res.status_code != 200:
                raise IOError('Non-successful response ({0}) accessing CAP URI at "{1}'.format(c_res, uri))
        except IOError as ioe:
            raise IOError('Trouble accessing CAP URI at "{0}: {1}'.format(uri, ioe.message))
        else:
            return c_res.text

    def json_to_csv_file(self, cap_as_json, res_file):

        try:
            json_parsed = json.loads(cap_as_json)
            cap_data = open(res_file, 'w')
            csvwriter = csv.writer(cap_data)
            count = 0
            for row in json_parsed:
                row['volume_24h_usd'] = row.pop('24h_volume_usd')  # BigQuery col names must start w/letters or symbols
                if count == 0:
                    header = row.keys()
                    csvwriter.writerow(header)
                    count += 1
                csvwriter.writerow(row.values())
            cap_data.close()
            return count

        except IOError as ioe:
            raise IOError('Trouble processing CAP data: {0}'.format(ioe.message))

if __name__ == '__main__':

    CAP_URI = 'https://api.coinmarketcap.com/v1/ticker/'
    CAP_RESULTS_FILE = '/Users/jonpowell/PycharmProjects/CasertaGoogleChallenge/CoinMarketCap.csv'

    reader = CoinMarketCapReader()
    cap_json = reader.read_market_cap_api(CAP_URI)
    num_recs = reader.json_to_csv_file(cap_json, CAP_RESULTS_FILE)

