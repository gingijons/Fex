
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup as soup

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
    cData= {
  "operationName": "Categories",
  "variables": {
    "last": 50,
    "level": 0
  },
  "query": "fragment CategoryFields on Category {\n  id\n  slug\n  name\n  description\n  backgroundImage {\n    alt\n    url\n    __typename\n  }\n  __typename\n}\n\nquery Categories($last: Int!, $level: Int) {\n  categories(last: $last, level: $level, onlyWithProducts: true) {\n    edges {\n      node {\n        ...CategoryFields\n        children(first: 30) {\n          edges {\n            node {\n              id\n              slug\n              name\n              children(first: 30) {\n                edges {\n                  node {\n                    id\n                    name\n                    slug\n                    __typename\n                  }\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    totalCount\n    __typename\n  }\n}\n"
}

    # response = requests.request(method="post", url=url, data = cData, headers=headers)

    response = requests.post("https://backend.kronan.is/graphql/", json=cData, headers=headers)
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
    data = json.load(open("Data/nettoCats.json"))
    print(pd.json_normalize(data))
    df = pd.DataFrame(data["model"])
    # for k, v in data['results'].items():
    #     print(k)


if __name__ == "__main__":
    getNetto()
    getNettoProds()