
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup as soup
from datetime import datetime
import time

today = datetime.today()

def getContent(url):
    headers = {'Content-type': 'application/json; charset=utf-8'}
    products = {
        "operationName": "products",
        "variables": {
            "first": 44,
            "categoryId": "01-00-00-avextir"
        },
        "query": "fragment ProductVariantFields on ProductVariant {\n  __typename\n  id\n  sku\n  name\n  measureCode\n  temporaryShortage\n  referenceWeightPerUnit\n  pricePerKilo {\n    __typename\n    amount\n  }\n  pricing {\n    onSale\n    discount {\n      gross {\n        amount\n        __typename\n      }\n      __typename\n    }\n    price {\n      gross {\n        amount\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  product {\n    baseComparisonUnit\n    qtyPerBaseCompUnit\n    __typename\n  }\n}\n\nquery products($first: Int!, $after: String, $categoryId: ID) {\n  products(\n    first: $first\n    after: $after\n    categories: [$categoryId]\n    categoriesIdIsSlug: true\n    sortBy: {field: KRONAN, direction: ASC}\n  ) {\n    totalCount\n    pageInfo {\n      endCursor\n      hasNextPage\n      __typename\n    }\n    edges {\n      node {\n        id\n        name\n        slug\n        attributes {\n          values {\n            id\n            name\n            slug\n            __typename\n          }\n          attribute {\n            name\n            slug\n            __typename\n          }\n          __typename\n        }\n        thumbnail {\n          url\n          alt\n          __typename\n        }\n        variants {\n          ...ProductVariantFields\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
    }
    cData = {
        "operationName": "Categories",
        "variables": {
            "last": 50,
            "level": 0
        },
        "query": "fragment CategoryFields on Category {\n  id\n  slug\n  name\n  description\n  backgroundImage {\n    alt\n    url\n    __typename\n  }\n  __typename\n}\n\nquery Categories($last: Int!, $level: Int) {\n  categories(last: $last, level: $level, onlyWithProducts: true) {\n    edges {\n      node {\n        ...CategoryFields\n        children(first: 30) {\n          edges {\n            node {\n              id\n              slug\n              name\n              children(first: 30) {\n                edges {\n                  node {\n                    id\n                    name\n                    slug\n                    __typename\n                  }\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    totalCount\n    __typename\n  }\n}\n"
    }

    # response = requests.request(method="post", url=url, data = cData, headers=headers)

    response = requests.post(
        "https://backend.kronan.is/graphql/", json=cData, headers=headers)
    return json.loads(response.content)
    # return response.content

def getkronan():
    c = getContent("https://backend.kronan.is/graphql/")
    # print(c)
    with open("Data/kronan.json",'w+', encoding='utf-8') as outfile:
        outfile.write(json.dumps(c, ensure_ascii=False, indent=1))

def getNetto():
    headers = {'Content-type': 'application/json; charset=utf-8'}
    cData= {
  "facetOptions": [],
  "offset": 0,
  "size": 9,
  "onlyOffers": False,
  "onlyBonus": False,
  "categories": [],
  "includeFacets": False,
  "sortBy": "",
  "term": "",
  "includeCategories": True,
  "hideOutOfStock": True
}

    # response = requests.request(method="post", url=url, data = cData, headers=headers)

    response = requests.post("https://app-commerce-prod-samkaup.azurewebsites.net/api/catalog/products/search", json=cData, headers=headers)
    # response = requests.get("https://netto.is/voerur/", headers=headers)
    print(response.content)
    res = json.loads(response.content)
    with open("Data/nettoCats.json",'w+', encoding='utf-8') as outfile:
        outfile.write(json.dumps(res['model'], ensure_ascii=False))


def getNettoProds():
    # with open("Data/nettoCats.json",'r', encoding='utf-8') as infile:
    #     data = pd.read_json(infile, lines=True, orient="columns")
    data = json.load(open("Data/nettoCats.json", encoding="utf8"))
    #print(pd.json_normalize(data))
    print(data['categories'])
    headers = {'Content-type': 'application/json; charset=utf-8'}
    prodsObj = []
    for i in data['categories']:
      print(i['displayName'])
      cData= {
        "facetOptions": [],
        "offset": 0,
        "size": 1000,
        "onlyOffers": False,
        "onlyBonus": False,
        "categories": [i['categoryId']],
        "includeFacets": False,
        "sortBy": "",
        "term": "",
        "includeCategories": False,
        "hideOutOfStock": True
      }
      response = requests.post("https://app-commerce-prod-samkaup.azurewebsites.net/api/catalog/products/search", json=cData, headers=headers)
      res = json.loads(response.content)
      res = res['model']
      print(len(res['results']))
      with open("Data/nettoProdsRaw.json",'w+', encoding='utf-8') as outfile:
          outfile.write(json.dumps(res, ensure_ascii=False, indent=1))
      for i in res['results']:
        tempObj = {
          'productNo': i['sku'],
          'name' : i['displayName'],
          "brand": i['brand'],
          "weight": i['weight'],
          "saleUnit": i['productTeaser'],
          "salesPrice": int(i['salesPrice'] or 0),
          "pricePerBigUnit": int(i['pricePerUnit'] or 0),
          "bigUnitOfMeasure": i['unitOfMeasure'],
          "categories" : '/'.join(x['name'] for x in i['breadcrumbs']),
          "image" : i['imageUrl'],
          "origin" : "Nettó",
          'originUrl' : i["url"],
          'lastScrape' : today
        }
        #print(tempObj)
        prodsObj.append(tempObj)
      
    with open("Data/nettoProds.json",'w+', encoding='utf-8') as outfile:
      outfile.write(json.dumps(prodsObj, ensure_ascii=False, indent=1))

    #df = pd.DataFrame(data["categories"])
    # for k, v in data['results'].items():
    #     print(k)

def getChild(data, count):
  print(count,data['node']['name'])
  try:
    for i in data['node']['children']['edges']:
      getChild(i, count + 1)
  except: 
    pass

def getKronanCatProds(cat):
  headers = {'Content-type': 'application/json; charset=utf-8'}
  products = {
      "operationName": "products",
      "variables": {
          "first": 300,
          "categoryId": cat
      },
      "query": "fragment ProductVariantFields on ProductVariant {\n  __typename\n  id\n  sku\n  name\n  measureCode\n  temporaryShortage\n  referenceWeightPerUnit\n  pricePerKilo {\n    __typename\n    amount\n  }\n  pricing {\n    onSale\n    discount {\n      gross {\n        amount\n        __typename\n      }\n      __typename\n    }\n    price {\n      gross {\n        amount\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  product {\n    baseComparisonUnit\n    qtyPerBaseCompUnit\n    __typename\n  }\n}\n\nquery products($first: Int!, $after: String, $categoryId: ID) {\n  products(\n    first: $first\n    after: $after\n    categories: [$categoryId]\n    categoriesIdIsSlug: true\n    sortBy: {field: KRONAN, direction: ASC}\n  ) {\n    totalCount\n    pageInfo {\n      endCursor\n      hasNextPage\n      __typename\n    }\n    edges {\n      node {\n        id\n        name\n        slug\n        attributes {\n          values {\n            id\n            name\n            slug\n            __typename\n          }\n          attribute {\n            name\n            slug\n            __typename\n          }\n          __typename\n        }\n        thumbnail {\n          url\n          alt\n          __typename\n        }\n        variants {\n          ...ProductVariantFields\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
  }
  response = requests.post("https://backend.kronan.is/graphql/", json=products, headers=headers)
  #print(response.content[0:1000])
  return json.loads(response.content)
  

def getkronanProds():
  data = json.load(open("Data/kronan.json", encoding="utf8"))
  #print(len(data['data']['categories']['edges']))
  prodsObj = []
  for i in data['data']['categories']['edges']:
    print("1",i['node']['name'])
    #print(i['node']['slug'])
    dt1 = datetime.fromtimestamp(time.time())
    for x in []
    res = getKronanCatProds(i['node']['slug'])
    print(len(res['data']['products']['edges']))
    dt2 = datetime.fromtimestamp(time.time())
    print(dt2-dt1)
    for j in res['data']['products']['edges']:
      p = j['node']
      v = p['variants'][0]
      #print(p['name'])
      tempObj = {
          'productNo': v['sku'],
          'name' : p['name'],
          "brand": None,
          "weight": v['product']['qtyPerBaseCompUnit'],
          "saleUnit": v['measureCode'],
          "salesPrice": int(v['pricing']['price']['gross']['amount'] or 0),
          "pricePerBigUnit": int(0),
          "bigUnitOfMeasure": v['product']['baseComparisonUnit'],
          "categories" : i['node']['name'],
          "image" : p['thumbnail']['url'],
          "origin" : "Krónan",
          'originUrl' : p["slug"],
          'lastScrape' : str(today)
        }
        #print(tempObj)
      prodsObj.append(tempObj)

    
    with open("Data/kronanProdsraw.json",'w+', encoding='utf-8') as outfile:
      outfile.write(json.dumps(res, ensure_ascii=False, indent=1))

  with open("Data/kronanProds.json",'w+', encoding='utf-8') as outfile:
      outfile.write(json.dumps(prodsObj, ensure_ascii=False, indent=1))
    # for j in i['node']['children']['edges']:
    #   getChild(j, 1)
    #   try:
    #     getChild(j['edges'], 10)
    #   except:
    #     pass
  
    # for j in i['node']['children']['edges']:
    #   print()



if __name__ == "__main__":
    #getNetto()
    #getNettoProds()
    #getkronan()
    getkronanProds()
