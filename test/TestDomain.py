from bs4 import BeautifulSoup
from lib.common.Util import *
from lib.common.URLHandler import *
import urllib.parse
import json


def get_properties_school():
    default_request_header = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }
    #G_DOMAIN_URL_SCHOOL = "https://www.domain.com.au/school-catchment/{0}"
    G_DOMAIN_URL_SCHOOL_TEST = "https://www.domain.com.au/schools/{0}?listingtype=forSale&pageno=35&ssubs=0"
    school_search = "templeton-primary-school-vic-3152-3750"
    url_templeton = G_DOMAIN_URL_SCHOOL_TEST.format(school_search)
    url_suburb_completion = "https://bettereducation.com.au/school/Primary/vic/vic_primary_school_rating.aspx/GetCompletionListLocality"
    response_content = requests.get(url_templeton, headers=default_request_header)
    debug_print(response_content.url)
    #debug_print(response_content.text)
    debug_print(response_content.status_code)

    rst_bs4 = BeautifulSoup(response_content.text, 'lxml')
    list_properties = rst_bs4.find_all('div', class_="nearby-properties__property nearby-properties__on-market-property")
    for each_property in list_properties:
        property_price_info = each_property.find('div', class_="nearby-properties__info-block nearby-properties__display-price")
        property_price = property_price_info.find('div', class_="nearby-properties__info-block-title").text.strip()
        debug_print(property_price)

        property_address_link = property_price_info.find('a', class_="nearby-properties__address-link")
        property_link = property_address_link["href"]
        debug_print(property_link)

        property_address_info = property_address_link.find('meta', itemprop="name")
        property_address = property_address_info["content"]
        debug_print(property_address)

        property_type_info = each_property.find('div', class_="nearby-properties__info-block nearby-properties__property-type")
        property_type_div = property_type_info.find('div', class_="nearby-properties__info-block-body")
        property_type = property_type_div.text.strip()
        debug_print(property_type)

        # beds, baths, car spaces
        property_feature_info = each_property.find('div', class_="nearby-properties__property-features-wrapper")
        list_features = property_feature_info.find_all("span", class_="property-feature__feature-text-container")
        index_figure = len(list_features)

        # beds
        if index_figure > 0 and list_features[0] is not None:
            property_bed = list_features[0].text.strip()
            debug_print(property_bed)

        # baths
        if index_figure > 1 and list_features[1] is not None:
            property_baths = list_features[1].text.strip()
            debug_print(property_baths)

        # car spaces
        if index_figure > 2 and list_features[2] is not None:
            property_car = list_features[2].text.strip()
            debug_print(property_car)








# Main test
if __name__ == '__main__':
    get_properties_school()
