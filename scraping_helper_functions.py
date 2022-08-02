import re
import requests

def available(pattern, found):
    if re.search(pattern, str(found)):
        return 1
    else:
        return 0

def isPagination(toggle, url, page, page_query_string):
    if not toggle:
        return url
    if toggle:
        return f'{url[:]}{page_query_string}{page}'

def paginationResponse(toggle, url, page, page_query_string):
    if toggle:
        tmp = f'{isPagination(toggle, url, page, page_query_string)}'
        activeUrl = f"f'{tmp}'"
        # print(activeUrl)
        return requests.get(eval(activeUrl))
    if not toggle:
        return requests.get(url)

def link_category(df, sub_category):
    return df['category'][df['link'] == sub_category].iloc[0]