import pandas as pd
from bs4 import BeautifulSoup
import json
import math
import codecs
from curl_cffi import requests as curlrq
import time
import asyncio
import re
import geoservices
import utils
# mostly constants
url_olx = "https://www.olx.com.br/imoveis/aluguel/estado-pe/grande-recife/recife?pe=1000&ret=1020&ret=1060&ret=1040&sd=3747&sd=3778&sd=3766&sd=3764&sd=3762"
url_wq = "https://www.webquarto.com.br/busca/quartos/recife-pe/Cordeiro%7CV%C3%A1rzea%7CTorre%7CTorr%C3%B5es%7CMadalena%7CIputinga?price_range%5B%5D=0,1000&has_photo=0&smokers_allowed=0&children_allowed=0&pets_allowed=0&drinks_allowed=0&visitors_allowed=0&couples_allowed=0"
url_mgf = "https://www.mgfimoveis.com.br/aluguel/quarto/pe-recife-cidade-universitaria?pricemax=1000"

# check if an ad already exists
def compareAds(ad: dict, prev_ads_urls: list):
    if ad.get('url') and ad.get('subject'):
        for url in prev_ads_urls:
            # print(url)
            if ad['url'] == url:
                return True
        return False

# Filters out ads sharing the same url
# todo: test behavior for empty and equal ads arrays
def filterAds(new_ads: list[dict], prev_ads: list):
    
    print(f'Filtering out ads...\n {len(new_ads)} ads to be matched against the {len(prev_ads)} previously stored ads')
    updatable_ads = []
    for i, curr_ad in enumerate(new_ads):
        if compareAds(curr_ad, prev_ads.get('url')):
            # update ad
            updatable_ads.append(new_ads.pop(i))
    print(f'\nNew ads: {len(new_ads)}\nUpdatable ads: {len(updatable_ads)}\n')
    return new_ads, updatable_ads

def makeSoup(url: str):
    content = curlrq.get(url, impersonate="chrome")
    soup = BeautifulSoup(content.text, "lxml")
    return soup

# Retorna a quantidade de páginas de resultados da busca
def findPagePropsOLX(soup):
    data_str = soup.find("script", {"id": "__NEXT_DATA__"}).get_text()
    props = json.loads(data_str)['props']['pageProps']
    return props

# Bottleneck here
def getCepOLX(url: str):
    soup = makeSoup(url)
    data_str = soup.find('script', string=re.compile(r'(?:dataLayer = )(\[(.*)\])')).get_text(strip=True)    
    return re.search(r'"zipcode":"(\d{8})"', data_str).group(1)

def parseAddress(cep: str):
    res = curlrq.get(f'viacep.com.br/ws/{cep}/json/').json()
    if res.get('erro'):
        return 'Endereço com CEP inválido.'
    return f'{res['logradouro']}, {res['bairro']}, {res['localidade']}'

def searchOLX():
    soup = makeSoup(url_olx)
    page_props = findPagePropsOLX(soup)
    pages_count = math.ceil(page_props['totalOfAds'] / page_props['pageSize'])
    
    ads = []
    unfiltereds = []
    for i in range(1, pages_count + 1):
        
        data = {}
        # Evita a repetição do scraper na página inicial
        if i == 1:
            data = page_props['ads']
        else:
            page_url = f'{url_olx}&o={i}'
            soup = makeSoup(page_url)
            page_props = findPagePropsOLX(soup)
            data = page_props['ads']
        unfiltereds.append(data)
        print(f"Got OLX page {i} data")
    
    # Flattening nested lists with ads
    unfiltereds = [ad for page in unfiltereds for ad in page]
    
    print('Processing ad data...')
    # Load previous ads
    # todo - replace csv for json, then sqlite database eventually
    prev_ads_urls = pd.read_csv('./data/old_data.csv').get('URL')
    prev_ads = pd.read_csv('./data/old_data.csv')
    filtereds, updatables = filterAds(unfiltereds, prev_ads)
    
    # todo - delete ads with broken url
    # todo - flag updatable ads to not go through the parseCoords function
    total_ads_count = 0
    current_ads_count = 0
    # todo - parsecoords in batch
    for i, ad in enumerate(filtereds):
        if ad.get("subject") is not None:
            # todo - def buildOlxAd(ad) function that appends (not overwrite) the data, but creates empty data initially
            cep = getCepOLX(ad['url'])
            addr = parseAddress(cep)
            coords = geoservices.parseCoords(cep)
            coords_split = []
            if len(coords) > 0:
                coords_split = coords.split(',')
            else:
                coords_split = [' ', ' ']
            actual_ad = {
                'url': ad['url'], 
                'title': ad['subject'],
                'thumbnail': ad['thumbnail'],
                'price': ad['price'],
                'address': addr if addr != 'Endereço com CEP inválido.' else ad['location'],
                'property_type': ad['category'],
                'latlng': coords,
                'lat': coords_split[0],
                'lng': coords_split[1],
                'active': True,
                'modifiedAt': utils.dateTimeNow()
            }
            ads.append(actual_ad)
        print(f"{i+1}/{total_ads_count} OLX ads have been processed")
    
    current_ads_count = len(filtereds)
    for i, ad in enumerate(updatables):
        # todo - def updateOlxAd(ad)
        if ad.get("subject") is not None:
            actual_ad = {
                'url': ad['url'], # don't update
                'title': ad['subject'],
                'thumbnail': ad['thumbnail'],
                'price': ad['price'],
                'address': addr if addr != 'Endereço com CEP inválido.' else ad['location'],
                'property_type': ad['category'],
                'latlng': coords, # get from prev_ads
                'lat': coords_split[0], # get from prev_ads
                'lng': coords_split[1], # get from prev_ads
                'active': True,
                'modifiedAt': utils.dateTimeNow()
            }
            ads.append(actual_ad)
        print(f"{current_ads_count+1+i}/{total_ads_count} OLX ads have been processed")
    
    # for i, ad in enumerate(unfiltereds):
    #     if ad.get("subject") is not None:
    #         cep = getCepOLX(ad['url'])
    #         addr = parseAddress(cep)
    #         coords = geoservices.parseCoords(cep)
    #         coords_split = []
    #         if len(coords) > 0:
    #             coords_split = coords.split(',')
    #         else:
    #             coords_split = [' ', ' ']
    #         actual_ad = {
    #             'url': ad['url'], 
    #             'title': ad['subject'],
    #             'thumbnail': ad['thumbnail'],
    #             'price': ad['price'],
    #             # 'address': d['location'],
    #             'address': addr if addr != 'Endereço com CEP inválido.' else ad['location'],
    #             'property_type': ad['category'],
    #             'latlng': coords,
    #             'lat': coords_split[0],
    #             'lng': coords_split[1],
    #             # 'zipcode': getCepOLX(d['url'])
    #         }
    #         ads.append(actual_ad)
    #         print(f"OLX ad {i} has been processed")
    
    
    return ads


# WQ multi-pages test url
# testing-only, keep commented out otherwise
# url_wq = "https://www.webquarto.com.br/busca/quartos/recife-pe?page=1&price_range[]=0,15000&has_photo=0&smokers_allowed=0&children_allowed=0&pets_allowed=0&drinks_allowed=0&visitors_allowed=0&couples_allowed=0"


def normalizeAdsPrices(ads: list[dict]):
    
    for ad in ads:
        price = ad['price']
        price = f'{price},00' if price.find(',') == -1 else price
        ad['price'] = price    
    
    return ads

def findDataWQ(raw):
    # target text between 'window.search' and 'window.search.city_name'
    for line in raw:
        content = line.get_text().strip()
        begin = "window.search = {"
        end = "window.search.city_name"
        if content.find(begin) > -1:
            end_idx = content.find(end)
            data_str = content[len(begin) - 1 : end_idx].strip()[:-1]
            rest_str = content[end_idx:]
            return data_str, rest_str
    return ""

def findPaginationWQ(src):
    arr = src.split(" = ")
    s = arr[3]
    end = s.find("window")
    s = s[:end - 4]
    return json.loads(s)

# Remove caracteres com encoding irrelevante
def sanitizeWQ(s):
    import ast, re, html
    
    # Remove caracteres unicode irrelevantes (emojis, etc.)
    #r = codecs.charmap_encode(re.sub(r'\\/', '/', s), 'ignore')[0].decode('unicode_escape')
    # r = codecs.charmap_encode(s, 'ignore')[0]#.decode('unicode_escape')
    r = re.sub(r'\\/', '/', s)
    charmap_tuple = codecs.charmap_encode(r, 'ignore')
    u_escaped = charmap_tuple[0].decode('unicode_escape', 'replace')
    
    # Remove surrogate pairs (html emojis (e.g.: '\ud83d\udc4', ' &#55356;&#57117;' ) )
    emojiless_str = re.sub(r'[\uD800-\uDFFF]', '', u_escaped)
    # r = re.sub(r'\\u[0-9a-fA-F]{4}', '', r)
    emojiless_str = re.sub(r'\\u[0-9a-fA-F]{4}', '', emojiless_str)
    # bullet point removal
    # emojiless_str = re.sub(r'&\#[a-zA-Z0-9]{1,5}', '', emojiless_str)
    result = emojiless_str
    result = re.sub(r"[\n\r]", r" ", result)
    
    # undef_chars = result.strip().split()
    # for w in undef_chars:
    #     print(w)
    # print(f'length: {len(undef_chars)}')
    return result

# parses string data from WebQuarto to JSON
def adsDataToJsonWQ(data_str):
    ads = []
    # set loads 'strict' arg to False to allow unescaped characters
    data = json.loads(data_str,strict=False)['ads']
    
    for d in data:
        # Compare and normalize both data shapes
        ad = {
            'url': d['url'], 
            'title': f"{d['title']}",# {d['description']}. {d['about_roommate']}",
            'thumbnail': d['main_photo'],
            'price': d['rent_price'],
            'address': f"{d['address']}, {d['location']}",
            'property_type': f"{d['property_type']}. {d['room_type']}",
            'latlng': f'{d['lat']},{d['lng']}',
            'lat': d['lat'],
            'lng': d['lng'],
            'active': True,
            'modifiedAt': utils.dateTimeNow()
        }
        ads.append(ad)
    return ads


def searchWQ():
    soup = makeSoup(url_wq)
    raw_scripts = soup.find_all("script")
    ads = []
    
    data_str, pagination = findDataWQ(raw_scripts)
    pagination = findPaginationWQ(pagination)
    data_str = sanitizeWQ(data_str)
    ads.append(adsDataToJsonWQ(data_str))
    print(f"WebQuarto Page 1 done")
    
    for i in range(pagination['last_page'] - 1):
        page_url = f"https://www.webquarto.com.br/busca/quartos/recife-pe?page={i + 1}&price_range[]=0,15000&has_photo=0&smokers_allowed=0&children_allowed=0&pets_allowed=0&drinks_allowed=0&visitors_allowed=0&couples_allowed=0"
        makeSoup(page_url)
        raw_scripts = soup.find_all("script")
        data_str, _ = findDataWQ(raw_scripts)
        data_str = sanitizeWQ(data_str)
        ads.append(adsDataToJsonWQ(data_str))
        print(f"WebQuarto Page {i+1} done")
    
    # Dados dos anúncios em flat list
    ads = [item for sublist in ads for item in sublist]
    return ads

def saveData(df: pd.DataFrame):
    df.to_json("data/data.json", columns=['Título', 'Tipo', 'Endereço', 'Preço', 'URL', 'lat', 'lng'])
    
    df = df.rename(columns={
        'url': 'URL', 'title': 'Título','thumbnail': 'Foto',
        'price': 'Preço','address': 'Endereço','property_type': 'Tipo',
        # 'latlng': 'Coordenadas'
    })
    # print(df.apply(lambda x: normalizeAdsPrices(x), axis=1, result_type='expand'))
    # print(df['Preço'])
    df.to_csv("data/data.csv", columns=['Título', 'Tipo', 'Endereço', 'Preço', 'URL', 'lat', 'lng'])
    
def makeDataFrame(data_arr: list, src: str):
    data_arr = normalizeAdsPrices(data_arr)
    
    serieses = []
    
    # print(f"Anúncios de Moradia encontrados na {src}:")
    for data in data_arr:
        s = pd.Series(data)
        serieses.append(s)
        # print(f"\n{s}\n")
    
    df = {}
    df = pd.DataFrame(serieses)
    return df
    # for i, data in enumerate(data_arr):    
    
    # print(data_arr[0])
    # df = pd.DataFrame({some_series: pd.Series.keys some_series.title}, index = some_series.index)
    # print(df)

async def scrapeAndPrint():
    running = True
    while running:
        curr_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        print(f"\nScraping now... ({curr_time})\n")
        
        dfWQ = makeDataFrame(searchWQ(), "WebQuarto")
        dfOLX = makeDataFrame(searchOLX(), "OLX")
        
        curr_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        print(f"\nScraping finished ({curr_time})\n")
        
        # concat DFs before saving
        df = pd.concat([dfWQ, dfOLX])
        saveData(df)
        # print(df)
        break
        await asyncio.sleep(60)

asyncio.run(scrapeAndPrint())
