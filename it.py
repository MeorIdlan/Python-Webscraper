import json

def extractItem(page,urls,q):
    print(f'Extracting item details: {q["query"]}')
    items = []
    for url in urls:
        print(f'Current URL: {url}')
        try:
            page.goto(url)
            page.wait_for_timeout(5 * 1000)
        except:
            continue

        # get all elements that contain json text of the current item
        jsons = page.locator('//script[@type="application/ld+json"]')
        jsonVal = None
        for i in range(jsons.count()):
            jsonVal = jsons.nth(i).inner_text()
            jsonVal = json.loads(jsonVal)
            if jsonVal['@type'] == 'Product':
                break
            else:
                jsonVal = None

        # if a json text is found regarding the item
        if jsonVal is not None:
            item = {}
            try:
                # get all details of item
                item['name'] = jsonVal['name'].strip()
                
                if type(jsonVal['brand']) is dict:
                    item['brand'] = jsonVal['brand']['name'].strip(' .')
                else:
                    item['brand'] = jsonVal['brand'].strip(' .')

                item['ratingCount'] = jsonVal['aggregateRating']['ratingCount']

                if jsonVal['offers']['@type'] == 'AggregateOffer':
                    item['price'] = min(jsonVal['offers']['lowPrice'], jsonVal['offers']['highPrice'])
                else:
                    item['price'] = jsonVal['offers']['price']

                item['url'] = jsonVal['url']

                # if item passes check, add to items to be returned
                if (itemCheck(item,q)):
                    print('Success. Appending.')
                    items.append(item)
                else:
                    print('Failed.')
            except KeyError as e:
                print(f'Metadata does not have {e}')

    return items
    
def itemCheck(item, q):
    # check item name
    nameList = q['query'].split()
    hit = 0
    for name in nameList:
        if name.lower() in ''.join(item['name'].lower().split()):
            hit += 1
    if hit / len(nameList) < 0.8:
        print('Item not relevant.')
        return False

    # check price range
    if float(item['price']) < q['minPrice'] or float(item['price']) > q['maxPrice']:
        print('Not in price range.')
        return False

    # check rating count
    if int(item['ratingCount']) < q['minRatingCount']:
        print('Not within minimum rating counts.')
        return False

    return True