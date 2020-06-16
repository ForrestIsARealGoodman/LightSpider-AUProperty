import requests
from requests import cookies
from lib.common.Util import *
from urllib.parse import urlparse
import time

G_HEADER_REAL_ESTATE = "real_estate_headers"
G_HEADER_DOMAIN = "domain_headers"
G_HEADER_BETTER_EDUCATION = "better_education_headers"
G_HEADER_DEFAULT = "real_estate_headers"

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


class URLHandlerClass:
    # class variable
    request_header_dict = dict()

    default_session = None
    current_header = None

    def __init__(self):
        pass

    @classmethod
    def get_content_from_html_with_type(cls, url, header_type=G_HEADER_DEFAULT):
        if header_type != G_HEADER_DEFAULT:
            request_header = default_request_header
            return cls.get_content_from_html(url, request_header)
        return False, None

    @classmethod
    def get_content_from_html(cls, url, header_data=default_request_header):
        result_flag = False
        get_response_content = None
        try:
            if cls.default_session is None or header_data != cls.current_header:
                cls.default_session = requests.session()
                cls.current_header = header_data
            get_response_content = cls.default_session.get(url, headers=header_data, timeout=60)
            get_response_content.raise_for_status()
            get_response_content.encoding = 'utf-8'
            result_content = get_response_content.text
            result_flag = True
        except requests.exceptions.HTTPError as err:
            result_content = "Http Error:" + str(err)
        except requests.exceptions.ConnectionError as err:
            result_content = "Error Connecting:" + str(err)
        except requests.exceptions.Timeout as err:
            result_content = "Timeout Error:" + str(err)
        except requests.exceptions.RequestException as err:
            result_content = "OOps, Something Else:" + str(err)

        if not result_flag:
            cls.default_session = None
            cls.current_header = None
        return result_content, result_flag

    @classmethod
    def get_response_from_html(cls, url, header_data=default_request_header):
        result_flag = False
        get_response_content = None
        try:
            if cls.default_session is None or header_data != cls.current_header:
                cls.default_session = requests.session()
                cls.current_header = header_data
            get_response_content = cls.default_session.get(url, headers=header_data, timeout=60)
            get_response_content.raise_for_status()
            get_response_content.encoding = 'utf-8'
            result_flag = True
        except requests.exceptions.HTTPError as err:
            result_content = "Http Error:" + str(err)
        except requests.exceptions.ConnectionError as err:
            result_content = "Error Connecting:" + str(err)
        except requests.exceptions.Timeout as err:
            result_content = "Timeout Error:" + str(err)
        except requests.exceptions.RequestException as err:
            result_content = "OOps, Something Else:" + str(err)

        if not result_flag:
            cls.default_session = None
            cls.current_header = None
        return get_response_content, result_flag

    @classmethod
    def post_content_from_html_with_type(cls, url, data_dict, header_type=G_HEADER_DEFAULT):
        if header_type != G_HEADER_DEFAULT:
            request_header = default_request_header
            return cls.post_content_from_html(url, request_header, data_dict)
        return False, None

    @classmethod
    def post_content_from_html(cls, url, data_dict, header_data=default_request_header):
        result_flag = False
        post_response_content = None
        try:
            if cls.default_session is None or header_data != cls.current_header:
                cls.default_session = requests.session()
                cls.current_header = header_data
            post_response_content = cls.default_session.post(url, headers=header_data, data=data_dict, timeout=60)
            post_response_content.raise_for_status()
            post_response_content.encoding = 'utf-8'
            result_content = post_response_content.text
            result_flag = True
        except requests.exceptions.HTTPError as err:

            result_content = "Http Error:" + str(err)
        except requests.exceptions.ConnectionError as err:
            result_content = "Error Connecting:" + str(err)
        except requests.exceptions.Timeout as err:
            result_content = "Timeout Error:" + str(err)
        except requests.exceptions.RequestException as err:
            result_content = "OOps, Something Else:" + str(err)

        if not result_flag:
            cls.default_session = None
            cls.current_header = None
        return result_content, result_flag

    @classmethod
    def get_host_url(cls, url):
        host_url = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
        return host_url


# Main test
if __name__ == '__main__':
    pass

