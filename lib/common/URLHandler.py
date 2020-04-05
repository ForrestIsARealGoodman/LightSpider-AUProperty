import requests
from requests import cookies
from lib.common.Util import *
from urllib.parse import urlparse
import time

G_HEADER_REAL_ESTATE = "real_estate_headers"

'''
USER_AGENTS = [
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/57.0.2987.110 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/61.0.3163.79 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
     'Gecko/20100101 '
     'Firefox/55.0'),  # firefox
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/61.0.3163.91 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/62.0.3202.89 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/63.0.3239.108 '
     'Safari/537.36'),  # chrome
]
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36
'''
class URLHandlerClass:

    # class variable
    cls_request_head_default = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'set-cookie': 'path=/; domain=.realestate.com.au',
        #'Host': 'www.realestate.com.au',
        #'Referer': 'https://www.realestate.com.au/buy/property-house-with-1-bedroom-in-Werribee%20VIC%203030/list-1?source=refinement&numBaths=1&',
        'referrer': 'https://www.realestate.com.au/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Cookie': 'reauid=0f8347687f450000746e885ece03000064fa0700; Country=AU; NM-_LKJ=3ad62fd0-cf03-1ed4-66b6-fc23f43ce19a; mid=11012324302806453344; Hint=i-0134d1c50e02091c2; s_fid=4B1BE004A0740EBC-0E28945851EDA30A; s_cc=true; AMCVS_341225BE55BBF7E17F000101%40AdobeOrg=1; _sp_ses.2fe7=*; s_ecid=MCMID%7C01785585626073332773502839180405418904; s_vi=[CS]v1|2F4437420515A011-40000924E20CE4AC[CE]; AMCV_341225BE55BBF7E17F000101%40AdobeOrg=-330454231%7CMCIDTS%7C18357%7CMCMID%7C01785585626073332773502839180405418904%7CMCAAMLH-1586604291%7C3%7CMCAAMB-1586604291%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1586006687s%7CNONE%7CMCAID%7C2F4437420515F816-400007A5C20D4141%7CvVersion%7C3.1.2; _fbp=fb.2.1585999498608.1854417477; VT_LANG=language%3Den-US; QSI_HistorySession=https%3A%2F%2Fwww.realestate.com.au%2Fbuy%2Fproperty-house-with-1-bedroom-in-Werribee%2520VIC%25203030%2Flist-1%3Fsource%3Drefinement%26numBaths%3D1%26~1585999537665; s_sq=%5B%5BB%5D%5D; QSI_SI_50fmRcIKsSzWlmZ_intercept=true; kmam_lapoz=m%2FYYngOJJTmqMTReWDy8tQ%3D%3D%3A%3A%2FIJu5skEpYRa5Pw%2BwHzUwTvM6AAYcLJ54xsZBiDIljWDr7W3BY3whjk9AVYeIjjHB9rQmc8S8BcoYrZqubNjxTsm5df21iYDsK9uGkWkQQDGB4ikaDqULUwIbGyxgvHfXcQ%2BaM7w2eUsBsyzA7nQw4tRpTgsjN2Qxc2NptoafM8FsUrMhivxGH7d6L2J6u9geHH1LqDbkTMV%2Fm%2BzpLI4qNw%2FRmvLwxToUgl23JjNvg2%2B1KBTdrAOgKE838zauljvUwussaEy4%2FbI1BFEr6p5Ppi0sGN4jpGEw%2FgUDfdbX%2BaJ9FPxkSnBhgVRn%2BC5OaDE9rY%2FYpr%2FFiV7u4FWJnSlxZgJpADOPwLA7FZQgL%2B8yxP%2B6aES18YfgAP6sPL4isDlkhxyJvAHYsFPKZLlb3ZgAx4YqWddM3lshG8KmCVlIMKsxiD2%2FwbZQ4iJ31inBNQX5MY6FOz8aADD7LBznggFsSs%2B6ndtu3aYrUGzAWYZ7h0TD%2FPspAtYD8OI81VuOs%2Bs%2BGs94v9DUOX58fFW9hs%2FTQ%3D%3D; utag_main=v_id:017144ef91c20015da71e6dcf09503073007d06b00bd0$_sn:1$_ss:0$_st:1586001910869$ses_id:1585999483333%3Bexp-session$_pn:4%3Bexp-session$vapi_domain:realestate.com.au$dc_visit:1$dc_event:8%3Bexp-session$dc_region:ap-southeast-2%3Bexp-session; _sp_id.2fe7=347647ec-90ca-4bfc-8f87-4aa5cd4f3191.1585999488.1.1586000112.1585999488.aa02933d-832e-4b69-9abe-910d8b22b997; External=%2FAPPNEXUS%3D4566801285870281179%2FCASALE%3DXn-7-osFVSQAAFdfOHAAAAB7%25269960%2FPUBMATIC%3D94A89238-A757-4353-AB43-D7ABAB6B88DD%2FRUBICON%3DK8CDHO67-Q-J9B%2F_EXP%3D1617536124%2F_exp%3D1617536127'
        }
    cls_session = None

    cls_request_head_dict = {}

    def __init__(self):
        pass

    @classmethod
    def get_cookie(cls, url):
        err_msg = None
        result_flag = False
        host_url = cls.get_host_url(url)
        if host_url in cls.cls_cookie:
            return cls.cls_cookie[host_url], True
        try:
            if cls.cls_session is None:
                cls.cls_session = requests.session()
            cookie_rst = cls.cls_session.get(host_url)
            cls.cls_cookie[host_url] = cls.cls_session.cookies
            result_flag = True
        except requests.exceptions.HTTPError as err:
            debug_print(cookie_rst.status_code)
            err_msg = "Http Error:" + str(err)
        except requests.exceptions.ConnectionError as err:
            err_msg = "Error Connecting:" + str(err)
        except requests.exceptions.Timeout as err:
            err_msg = "Timeout Error:" + str(err)
        except requests.exceptions.RequestException as err:
            err_msg = "OOps, Something Else:" + str(err)

        if not result_flag:
            return err_msg, result_flag
        cookie_dict = {}
        for cookie in cls.cls_common_cookie.split(";"):
            key, value = cookie.split('=', 1)
            cookie_dict[key] = value
        return cookie_dict, True

    @classmethod
    def get_content_from_html(cls, url, request_header_type):
        result_flag = False
        try:
            if cls.cls_session is None:
                cls.cls_session = requests.session()
            header_object = cls.cls_request_head_default
            if request_header_type in cls.cls_request_head_dict.keys():
                header_object = cls.cls_request_head_dict[request_header_type]
            response_content = cls.cls_session.get(url, headers=header_object, timeout=60)
            response_content.raise_for_status()
            response_content.encoding = 'utf-8'
            result_content = response_content.text
            result_flag = True
        except requests.exceptions.HTTPError as err:
            debug_print(response_content.status_code)
            result_content = "Http Error:" + str(err)
        except requests.exceptions.ConnectionError as err:
            result_content = "Error Connecting:" + str(err)
        except requests.exceptions.Timeout as err:
            result_content = "Timeout Error:" + str(err)
        except requests.exceptions.RequestException as err:
            result_content = "OOps, Something Else:" + str(err)

        if not result_flag:
            cls.cls_session = None
        return result_content, result_flag

    @classmethod
    def get_host_url(cls, url):
        host_url = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
        return host_url



# Main test
if __name__ == '__main__':
    url_test_host = "https://www.realestate.com.au/"
    url_test = "https://www.realestate.com.au/buy/with-2-bedrooms-between-75000-2250000-in-ringwood,+vic+3134/list-1?maxBeds=5&source=refinement"
    url_candidate = "https://suggest.realestate.com.au/consumer-suggest/suggestions?max=7&query=werribe&type=suburb%2Cprecinct%2Cregion%2Cstate%2Cpostcode&src=homepage"
    #"https://www.realestate.com.au/buy/property-house-with-2-bedroom-in-Werribee VIC 3030/list-1?source=refinement&numBaths=2&"

    request_header = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Referer': 'https://www.realestate.com.au/buy/property-house-with-1-bedroom-in-Werribee%20VIC%203030/list-1?source=refinement&numBaths=1&',
        'Upgrade-Insecure-Requests': '1',
        'set-cookie': 'path=/; domain=.realestate.com.au',
        #'Host': 'www.realestate.com.au',
        'Cookie': 'reauid=0f8347687f450000746e885ece03000064fa0700; Country=AU; NM-_LKJ=3ad62fd0-cf03-1ed4-66b6-fc23f43ce19a; mid=11012324302806453344; Hint=i-0134d1c50e02091c2; s_fid=4B1BE004A0740EBC-0E28945851EDA30A; s_cc=true; AMCVS_341225BE55BBF7E17F000101%40AdobeOrg=1; _sp_ses.2fe7=*; s_ecid=MCMID%7C01785585626073332773502839180405418904; s_vi=[CS]v1|2F4437420515A011-40000924E20CE4AC[CE]; AMCV_341225BE55BBF7E17F000101%40AdobeOrg=-330454231%7CMCIDTS%7C18357%7CMCMID%7C01785585626073332773502839180405418904%7CMCAAMLH-1586604291%7C3%7CMCAAMB-1586604291%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1586006687s%7CNONE%7CMCAID%7C2F4437420515F816-400007A5C20D4141%7CvVersion%7C3.1.2; _fbp=fb.2.1585999498608.1854417477; VT_LANG=language%3Den-US; QSI_HistorySession=https%3A%2F%2Fwww.realestate.com.au%2Fbuy%2Fproperty-house-with-1-bedroom-in-Werribee%2520VIC%25203030%2Flist-1%3Fsource%3Drefinement%26numBaths%3D1%26~1585999537665; s_sq=%5B%5BB%5D%5D; QSI_SI_50fmRcIKsSzWlmZ_intercept=true; kmam_lapoz=m%2FYYngOJJTmqMTReWDy8tQ%3D%3D%3A%3A%2FIJu5skEpYRa5Pw%2BwHzUwTvM6AAYcLJ54xsZBiDIljWDr7W3BY3whjk9AVYeIjjHB9rQmc8S8BcoYrZqubNjxTsm5df21iYDsK9uGkWkQQDGB4ikaDqULUwIbGyxgvHfXcQ%2BaM7w2eUsBsyzA7nQw4tRpTgsjN2Qxc2NptoafM8FsUrMhivxGH7d6L2J6u9geHH1LqDbkTMV%2Fm%2BzpLI4qNw%2FRmvLwxToUgl23JjNvg2%2B1KBTdrAOgKE838zauljvUwussaEy4%2FbI1BFEr6p5Ppi0sGN4jpGEw%2FgUDfdbX%2BaJ9FPxkSnBhgVRn%2BC5OaDE9rY%2FYpr%2FFiV7u4FWJnSlxZgJpADOPwLA7FZQgL%2B8yxP%2B6aES18YfgAP6sPL4isDlkhxyJvAHYsFPKZLlb3ZgAx4YqWddM3lshG8KmCVlIMKsxiD2%2FwbZQ4iJ31inBNQX5MY6FOz8aADD7LBznggFsSs%2B6ndtu3aYrUGzAWYZ7h0TD%2FPspAtYD8OI81VuOs%2Bs%2BGs94v9DUOX58fFW9hs%2FTQ%3D%3D; utag_main=v_id:017144ef91c20015da71e6dcf09503073007d06b00bd0$_sn:1$_ss:0$_st:1586001910869$ses_id:1585999483333%3Bexp-session$_pn:4%3Bexp-session$vapi_domain:realestate.com.au$dc_visit:1$dc_event:8%3Bexp-session$dc_region:ap-southeast-2%3Bexp-session; _sp_id.2fe7=347647ec-90ca-4bfc-8f87-4aa5cd4f3191.1585999488.1.1586000112.1585999488.aa02933d-832e-4b69-9abe-910d8b22b997; External=%2FAPPNEXUS%3D4566801285870281179%2FCASALE%3DXn-7-osFVSQAAFdfOHAAAAB7%25269960%2FPUBMATIC%3D94A89238-A757-4353-AB43-D7ABAB6B88DD%2FRUBICON%3DK8CDHO67-Q-J9B%2F_EXP%3D1617536124%2F_exp%3D1617536127'
        }
    request_params = {
        'source': 'refinement',
        'numBaths': '1'
    }
    retry_count = 0
    test_session = requests.session()
    while retry_count < 3:
        print("[{0}]th try...".format(retry_count+1))
        retry_count += 1
        response = test_session.get(url_test, headers=request_header, timeout=60)
        #debug_print(response.text)
        debug_print(response.status_code)
        SleeperClass.sleep_random()


    '''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"')

    #chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    #browser = webdriver.Chrome(options=chrome_options)
    browser = webdriver.PhantomJS(executable_path=r'C:\Program Files (x86)\Python3\Scripts\phantomjs.exe')
    browser.get(url_test)
    debug_print(browser.page_source)
    '''
    '''
    content, flag = URLHandlerClass.get_content_from_html(url_test)
    debug_print(content)
    debug_print(flag)
    URLHandlerClass.cls_session = requests.Session()
    for cookie in cookies_list:
        URLHandlerClass.cls_session.cookies.set(cookie['name'], cookie['value'])

    request_header = {
        'host': 'www.realestate.com.au',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    url_test = "https://www.realestate.com.au/buy/property-house-with-1-bedroom-in-Werribee VIC 3030/list-1?source=refinement&numBaths=1&"
    response_content = URLHandlerClass.cls_session.get(url_test, headers=request_header, timeout=5)
    response_content.raise_for_status()
    debug_print(response_content)
    #"https://whatismyipaddress.com/"
        #"https://www.realestate.com.au/rent/property-house-with-1-bedroom-in-Werribee, VIC 3030/list-1?source=refinement&numBaths=1&"
    #content, flag = URLHandlerClass.get_content_from_html(url_test)
    #debug_print(content)
    #debug_print(flag)
    cookies_dict = {}
    for cookie in cookies_list:
        cookies_dict[cookie['name']] = cookie['value']
        debug_print(cookie)
    '''

