def extractUrl(page, q, count):
    print(f'Extracting URL: {q["query"]}')
    brands = getBrandsShopee(page,q,count)
    urls = extractUrlShopee(page,q,brands)
    return urls

def extractUrlShopee(page, q, brands):
    print('Extracting URLs from Shopee...')
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
            page.wait_for_timeout(5 * 1000)
            try:
                page.locator('.shopee-search-empty-result-section__title', has_text='No results found').click(timeout=3*1000, trial=True)
                return []
            except:
                pass
        except:
            print('Something went wrong while opening the page. Continuing to next page.')
            continue

        for _ in range(5):
            page.mouse.wheel(0,1500)
            page.wait_for_timeout(5 * 1000)

        all_items = page.locator('.shopee-search-item-result__item')
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
        page.wait_for_timeout(5 * 1000)
    except:
        return []

    # get all elements that has brand name
    div = page.locator('//div[@class="shopee-filter-group shopee-brands-filter"]').locator('//label[@class="shopee-checkbox__control"]')

    # from elements, get all brand names and corresponding id
    brands = {}
    for i in range(div.count()):
        brands[div.nth(i).locator('span').inner_text().lower()] = div.nth(i).locator('input').get_attribute('value')
    
    return brands