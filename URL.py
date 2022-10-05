import re

def extractUrl(page, q, count):
    print(f'Extracting URL: {q["query"]}')
    site = q['site']

    if site.lower() == 'lazada':
        brands = getBrandsLazada(page,q)
        urls = extractUrlLazada(page,q,brands)
    elif site.lower() == 'shopee':
        brands = getBrandsShopee(page,q,count)
        urls = extractUrlShopee(page,q,brands)
    elif site.lower() == 'both':
        brandsLazada = getBrandsLazada(page,q)
        brandsShopee = getBrandsShopee(page,q,count)
        urls = extractUrlLazada(page,q,brandsLazada)
        urls.extend(extractUrlShopee(page,q,brandsShopee))
    else:
        return []
    return urls

def extractUrlLazada(page, q, brands):
    print('Extracting from Lazada...')
    query = q['query'].replace(' ', '%20')
    stars = q['stars']
    pages = q['pages']
    minPrice = q['minPrice']
    maxPrice = q['maxPrice']
    brandsToSearch = q['brand']

    # setting base url
    base_url = 'https://www.lazada.com.my/'

    # adding brands to url
    if len(brandsToSearch) == 0 or len(brands) == 0:
        base_url += 'catalog/?'
    else:
        for count,brand in enumerate(brandsToSearch):
            for lazadaBrand in brands:
                if brand in lazadaBrand.replace('-',' '):
                    if count == 0:
                        base_url += f'{lazadaBrand}'
                    else:
                        base_url += f'--{lazadaBrand}'
                    break

    # adding rest of the query to url
    base_url += f'/?q={query}&rating={stars}&price={minPrice}-{maxPrice}'

    # extract all urls in page
    urls = []
    for i in range(pages):
        full_url = f'{base_url}&page={i+1}'
        try:
            page.goto(full_url)
        except:
            continue

        for _ in range(4):
            page.mouse.wheel(0,1500)
            page.wait_for_timeout(3 * 1000)

        all_items = page.locator('//div[@class="_95X4G"]')
        for j in range(all_items.count()):
            urls.append(f'https:{all_items.nth(j).locator("a").get_attribute("href")}')

    return urls

def getBrandsLazada(page, q):
    print('Getting Lazada Brand Names...')
    # go to page with url
    url = f'https://www.lazada.com.my/catalog/?q={q["query"].replace(" ","%20")}&rating={q["stars"]}&page=1&price={q["minPrice"]}-{q["maxPrice"]}'
    try:
        page.goto(url)
        page.wait_for_timeout(10 * 1000)
    except:
        return []

    # get element that has all brands
    divs = page.locator('//div[@class="gJ98q"]').filter(has=page.locator('._9xWFp:has-text("Brand")'))

    for i in range(divs.count()):
        text = divs.nth(i).locator('._9xWFp').inner_text()
        if text == 'Brand':
            divs = divs.nth(i)
            break

    # get indexes of all links
    indicator = '<a href="https://www.lazada.com.my/'
    indexes = [m.start() for m in re.finditer(indicator, divs.inner_html())]
    
    # get brand names from links
    brands = [divs.inner_html()[idx+len(indicator):divs.inner_html().find('/', idx + len(indicator) + 1)].lower() for idx in indexes]
    return brands

def extractUrlShopee(page, q, brands):
    print('Extracting from Shopee...')
    query = q['query'].replace(' ', '%20')
    stars = q['stars']
    pages = q['pages']
    minPrice = q['minPrice']
    maxPrice = q['maxPrice']
    brandsToSearch = q['brand']

    # setting base url
    base_url = 'https://www.shopee.com.my/search?'

    # adding brands to url
    if len(brandsToSearch) != 0 and len(brands) != 0:
        for count,brand in enumerate(brandsToSearch):
            for shopeeBrand in brands:
                if brand in shopeeBrand.replace('-',' '):
                    if count == 0:
                        base_url += f'brands={brands[shopeeBrand]}'
                    else:
                        base_url += f'%2C{brands[shopeeBrand]}'
                    break

    # adding rest of query to url
    base_url += f'&keyword={query}&ratingFilter={stars}&maxPrice={maxPrice}&minPrice={minPrice}'

    # extract all url in page
    urls = []
    for i in range(pages):
        full_url = f'{base_url}&page{i}'
        try:
            page.goto(full_url)
        except:
            continue

        for _ in range(4):
            page.mouse.wheel(0,1500)
            page.wait_for_timeout(3 * 1000)

        all_items = page.locator('//div[@class="col-xs-2-4 shopee-search-item-result__item"]')
        for j in range(all_items.count()):
            urls.append(f'https://www.shopee.com.my{all_items.nth(j).locator("a").get_attribute("href")}')

    return urls

def getBrandsShopee(page, q, count):
    print('Getting Shopee Brand Ids...')
    # go to page with url
    url = f'https://www.shopee.com.my/search?keyword={q["query"].replace(" ","%20")}&page=1&ratingFilter={q["stars"]}&maxPrice={q["maxPrice"]}&minPrice={q["minPrice"]}'
    
    try:
        page.goto(url)
        # click on language if first time opening shopee website
        if count == 0:
            page.locator('//button[@class="shopee-button-outline shopee-button-outline--primary-reverse"]', has_text='English').click()
        page.wait_for_timeout(3 * 1000)
    except:
        return []

    # get all elements that has brand name
    div = page.locator('//div[@class="shopee-filter-group shopee-brands-filter"]').locator('//label[@class="shopee-checkbox__control"]')

    # from elements, get all brand names and corresponding id
    brands = {}
    for i in range(div.count()):
        brands[div.nth(i).locator('span').inner_text().lower()] = div.nth(i).locator('input').get_attribute('value')
    
    return brands