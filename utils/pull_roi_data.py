import requests
'''
-----------------------------------------------------------
Pull list of properties from Property Finder via search query
-----------------------------------------------------------
Parameters:
    query: location string to serach
Returns:
    array: array of property data
-----------------------------------------------------------
'''
def fetch_properties_property_finder(query: str):
    base_url = "https://www.propertyfinder.ae/_next/data/RpCipljjnoqvWwtxQZXaf/en/transactions/buy/dubai"
    url = f"{base_url}/{query}.json"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        json_data = response.json()
        transaction_list = json_data['pageProps']['list']['transactionList']
        return transaction_list
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"JSON Error: {e}")
        print("Response content:", response.text)

    return list()

'''
-----------------------------------------------------------
This function is used to pull sales data from Property Finder for various time periods
-----------------------------------------------------------
Parameters:
    None
Returns:
    dict: dictionary of sales data for various time periods
-----------------------------------------------------------
'''
def fetch_sales_data_property_finder():
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    base_url = "https://www.propertyfinder.ae/_next/data/RpCipljjnoqvWwtxQZXaf/en/transactions/buy/dubai/jumeirah.json"
    periods = ["ytd", "1w", "1m", "3m", "6m", "1y", "3y"]
    data = {}
    for period in periods:
        url = f"{base_url}?period={period}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            data[period] = json_data['pageProps']['insights']['insights']
        else:
            data[period] = "Failed to fetch data"
    return data



def fetch_properties_bayut(query: str):
    # format str to remove spaces and replace with hypehns
    query = query.replace(" ", "-")
    base_url = "https://www.bayut.com/api/internalLinks/propertyMarketAnalysisPage/?purpose=for-sale&location=/dubai/"
    url = f"{base_url}/{query}.json"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        json_data = response.json()
        #transaction_list = json_data['pageProps']['list']['transactionList']
        return json_data
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"JSON Error: {e}")
        print("Response content:", response.text)

    return list()


if __name__ == "__main__":
    print('requesting property finder...')
    print(fetch_properties_property_finder("jumeirah-golf-estates"))
    input()
    print('requesting bayut...')
    print(fetch_properties_bayut("jumeirah-golf-estates"))
    input()
    print('requesting sales data...')
    print(fetch_sales_data_property_finder())
    