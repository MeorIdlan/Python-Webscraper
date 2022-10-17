from math import ceil
import utility

def extractItem(page,urls,q):
    print(f'Extracting item details: {q["query"]}')
    items = []
    for url in urls:
        item = {}
        print(f'\nCurrent URL: {url}')
        try:
            page.goto(url)
            page.wait_for_timeout(5 * 1000)
            while '/login?' in page.url:
                page.goto(url)
                page.wait_for_timeout(5 * 1000)
        except:
            continue

        # get all details
        # NAME
        item['name'] = page.locator('._2rQP1z').locator('span').inner_text().strip()
        if not itemCheckName(item['name'], q):
            print('Failed.')
            continue

        # BRAND
        prodSpecs = page.locator('.OktMMO')
        item['brand'] = ''
        for i in range(prodSpecs.count()):
            if prodSpecs.nth(i).locator('label').inner_text().lower() == 'brand':
                item['brand'] = prodSpecs.nth(i).locator('a').inner_text()

        # RATINGS
        item['ratingCount'] = page.locator('._3y5XOB').last.inner_text()
        if not itemCheckRatings(item['ratingCount'], q):
            print('Failed.')
            continue

        # PRICE
        # check if item has variations
        hasVar = checkVariation(page)
        # if theres variation
        if hasVar:
            print('Item has variations. Retrieving a relevant variation.')
            # get the relevant variation
            resultVars = getVariation(page)
            # if there is a None in result, go to next url
            # else, get price of variation
            if None in resultVars.values():
                print('Skipping item.')
                continue
            else:
                item['price'] = getVariationPrice(page, resultVars)
        else:
            item['price'] = page.locator('._2Shl1j').inner_text()

        if not itemCheckPrice(float(item['price'].replace('RM', '').replace(',', '')), q):
            print('Failed.')
            continue

        # URL
        item['url'] = url

        print('Success. Appending item:')
        print(f'\tName: {item["name"]}')
        print(f'\tBrand: {item["brand"]}')
        print(f'\tRatings: {item["ratingCount"]}')
        print(f'\tPrice: {item["price"]}')
        print(f'\tURL: {item["url"]}')

        items.append(item)

    return items

def itemCheckName(itemName, q):
    # check important tags first
    mustHitTags = q['mustHitTags']
    for tag in mustHitTags:
        if tag.lower() not in ''.join(itemName.lower().split()):
            print(f'Item did not hit priority tag: {tag}.')
            return False

    # check relevance through query string
    nameList = q['query'].split()
    hit = 0
    for name in nameList:
        if name.lower() in ''.join(itemName.lower().split()):
            hit += 1

    # if not majority hits, return false
    if hit < ceil(len(nameList)/2):
        print('Item not relevant.')
        return False
    return True

def itemCheckPrice(itemPrice, q):
    if float(itemPrice) < q['minPrice'] or float(itemPrice) > q['maxPrice']:
        print('Not in price range.')
        return False
    return True

def itemCheckRatings(itemRatingCount, q):
    if int(itemRatingCount) < q['minRatingCount']:
        print('Not within minimum rating counts.')
        return False
    return True

def checkVariation(page):
    try:
        page.locator('._3Bh7nx').first.click(timeout=3*1000, trial=True)
        return True
    except:
        return False

def getVariation(page):
    resultVars = {'rows': 0}
    allRowsLabel = page.locator('._1RCFQu').locator('._34CHXV')
    allRows = page.locator('._1RCFQu').locator('._3Bh7nx')
    for i in range(allRows.count()):
        row = allRows.nth(i)
        rowVariations = row.locator('.product-variation')

        vars = []

        # only add variations that are in stock
        # i.e. button is not disabled
        for j in range(rowVariations.count()):
            var = rowVariations.nth(j)
            if var.get_attribute('aria-disabled') == 'false':
                vars.append(var)

        # print all available variations
        print(f'Please select a variation for {allRowsLabel.nth(i).inner_text()}:')
        for j,var in enumerate(vars):
            print(f'\t{j+1}. {var.get_attribute("aria-label")}')

        # ask input

        utility.notify()
        varSelect = int(input('Enter a number (0 if not selecting any, this will skip this item)(ex: 1): '))
        while varSelect < 0 or varSelect > len(vars):
            varSelect = int(input('Enter a valid number (0 if not selecting any, this will skip this item)(ex: 1): '))

        # add the selected variation to resultVars
        if varSelect != 0:
            resultVars['rows'] += 1
            resultVars[i] = vars[varSelect-1]
        else:
            resultVars[i] = None
            break
    return resultVars

def getVariationPrice(page, resultVars):
    for i in range(resultVars['rows']):
        var = resultVars[i]
        var.click()
        page.wait_for_timeout(1 * 1000)
    price = page.locator('._2Shl1j').inner_text()

    return price