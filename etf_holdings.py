# This program gets the holdings of a specified ETF from www.barchart.com
# and computes the actual equity you have for each company.
# At the end of the operation, the program saves this information into .csv file
# and shows you bar plot.

import argparse
import pandas as pd
import matplotlib.pyplot as plt
# from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from bs4 import BeautifulSoup

def get_etf_holdings(etf_symbol, total_equity):
    '''
    etf_symbol: str
    
    return: pd.DataFrame
    '''
    url = 'https://www.barchart.com/stocks/quotes/{}/constituents?page=all'.format(
        etf_symbol)

    # Loads the ETF constituents page and reads the holdings table
    browser = WebDriver() 
    # options = webdriver.ChromeOptions()           # Codes to not open the browser. However, generated messy warnings.
    # options.add_argument('headless')
    # browser = webdriver.Chrome(chrome_options=options)
    browser.get(url)
    html = browser.page_source
    # BeautifulSoup is a webscraping tool
    soup = BeautifulSoup(html, 'html')
    table = soup.find("div", {"class":"bc-table-scrollable-inner"})

    # Reads the holdings table line by line and appends each asset to a
    # dictionary along with the holdings percentage
    asset_dict = {}
    for row in table.select('tr')[1:-1]:
        try:
            cells = row.select('td')
            symbol = cells[0].get_text().strip()
            name = cells[1].text.strip()
            name_splitted = name.split()
            name_first = name_splitted[0]
            if symbol=="":
                symbol = name_first         # foreign stocks don't have symbol. Use the first word in the name instead.
            celltext = cells[2].get_text().strip()
            percent = float(celltext.rstrip('%'))
            equity = total_equity*percent/100.0
            if symbol!="" and percent!=0.0:
                asset_dict[symbol] = {
                    'name': name,
                    'percent': percent,
                    'equity': equity,
                }
        except BaseException as ex:
            print(ex)
    # browser.quit()
    return pd.DataFrame.from_dict(asset_dict, orient='index')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("etf", help="Name of ETF")
    parser.add_argument("equity", help="Amount you own", type=float)
    args = parser.parse_args()

    df = get_etf_holdings(args.etf, args.equity)
    df.sort_values(by='equity', axis=0, ascending=False,
                    inplace=True, na_position='last')
    csv_name = args.etf+'.csv'
    df.to_csv(csv_name, sep='\t')

    # Plotting
    ax = df.plot.bar(y='equity')
    # plt.xticks(rotation=45)
    plt.xlabel('Companies')
    plt.ylabel('Equity')
    plt.grid()
    plt.show()

if __name__ == "__main__":
    main()
