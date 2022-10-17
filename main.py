import json
import URL
import it
import pandas as pd
import utility
from playwright.sync_api import sync_playwright

def main():
    # open an input file
    jsonFile = open(f'./inputs/input10.json')
    queries = json.loads(jsonFile.read())
    jsonFile.close()

    with sync_playwright() as p:
        # launch browser and open a new page
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # for each queries, extract all details
        for count,q in enumerate(queries):
            print(f'Current query: {q["query"]}')
            # extract all item pages
            urls = URL.extractUrl(page,q,count)
            if len(urls) > 0:
                # extract details of item from all item pages
                items = it.extractItem(page,urls,q)
                if len(items) > 0:
                    # convert to a dataframe and remove duplicates
                    df = pd.DataFrame.from_dict(items)
                    df.drop_duplicates(subset='url',keep='first')
                    # create a csv file to store all item details
                    utility.createCSV(df,q['query'])
            else:
                print('No URLs found. Moving on to next query.')

        browser.close()

if __name__ == '__main__':
    main()