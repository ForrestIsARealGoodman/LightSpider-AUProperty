from bs4 import BeautifulSoup
from lib.common.Util import *
from lib.common.URLHandler import *
import urllib.parse
import json


def get_candidate_suburbs():
    default_header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Content-Length': '50',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    url_suburb_completion = "https://bettereducation.com.au/school/Primary/vic/vic_primary_school_rating.aspx/GetCompletionListLocality"
    payload_suburbs = {
        "count": '10',
        "contextKey": "null"
    }
    payload_suburbs["prefixText"] = "WANTIRNA"
    data_suburbs = json.dumps(payload_suburbs)




    '''
    data_suburbs = dict()
    data_suburbs["prefixText"] = "WANTIRNA"
    data_suburbs["count"] = "10"
    data_suburbs["contextKey"] = "null"
    '''


    response_content = requests.post(url_suburb_completion, data=data_suburbs, headers=default_header)
    debug_print(response_content.text)
    debug_print(response_content.status_code)

    data_response = json.loads(response_content.text)
    debug_print(data_response)
    data_response_list = data_response["d"]
    debug_print(data_response_list)
    for each_candidate in data_response_list:
        debug_print(each_candidate)
        debug_print(type(each_candidate))
        data_candidate = json.loads(each_candidate)
        for key, value in data_candidate.items():
            if key == "First":
                debug_print(value)


def get_candidate_schools():
    better_education_base_url = "https://bettereducation.com.au/"
    default_header_be = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '941',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'ASP.NET_SessionId=kvpzxiipirirlo3kpkdktxjw; ARRAffinity=b1b2b593af00ca6fbf5d71ca9df8e68c3c120f5dc0623dcab2156c5e4d149dc4; _ga=GA1.3.517864818.1591071459; __gads=ID=6b7f47076135d0b3:T=1591071460:S=ALNI_Mbuo1izUuPa_tUT60Q06vKoRQHzHQ; .ASPXAUTH=2446767BE2AA58760CA16F6D4DD16930A0FDE9B4D0D86A2ABBB7E006F499B4C6E9D6D330C8CDA04F370416D3DEB85FAFF46E43A7891EF3DD93F6BCE025C1167A1AAED117A57DF017474280EE444B0ADB9E0E3DE674924C6599B37BEB7F7BDEDE232166E3A0440F55634E8FDF9C5211FF6DF2ECD8A012D9A36C70D5394AA36496949F85AF354DE963B50EB50D446EDA146121472E; PreviousVisit=6/10/2020 2:13:17 PM; _gid=GA1.3.264798830.1592033612',
        'Host': 'bettereducation.com.au',
        'Origin': 'https://bettereducation.com.au',
        'Referer': 'https://bettereducation.com.au/school/Primary/vic/vic_primary_school_rating.aspx',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'X-MicrosoftAjax': 'Delta=true',
        'X-Requested-With': 'XMLHttpRequest'
    }
    default_header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '941',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }
    url_suburb_completion = "https://bettereducation.com.au/school/Primary/vic/vic_primary_school_rating.aspx"

    data_raw = 'ctl00%24ContentPlaceHolder1%24ToolkitScriptManager2=ctl00%24ContentPlaceHolder1%24UpdatePanel3%7Cctl00%24ContentPlaceHolder1%24TextBoxLocality&__PREVIOUSPAGE=BPuP9uKzo4XlP9V40uRnjPu4wNB5CHd9aCJA8XsDEzDH_6LhAnEqwwv_t2Ia5vymxAenV_uGPGtj8A0duXdrdoHexzelJN3mK1eYlKC6fSNGUtatOq26oYEY_1fWIs9fJRLvmaJsHbKgKe0GjElYRxWmCKM1&ctl00%24ContentPlaceHolder1%24TextBoxSchool=&ctl00%24ContentPlaceHolder1%24TextBoxLocality={0}&ctl00%24ContentPlaceHolder1%24TextBoxRadius=&hiddenInputToUpdateATBuffer_CommonToolkitScripts=1&__EVENTTARGET=ctl00%24ContentPlaceHolder1%24TextBoxLocality&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%2FwEPDwUKMTIwMjU3ODMwMWQYAgUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgIFI2N0bDAwJExvZ2luVmlldzEkTG9naW5TdGF0dXMxJGN0bDAxBSNjdGwwMCRMb2dpblZpZXcxJExvZ2luU3RhdHVzMSRjdGwwMwUjY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSRHcmlkVmlldzEPPCsADAEIZmRJji5QFtzlyXDVdUnh7mtgaKbCbA%3D%3D&__VIEWSTATEGENERATOR=6E03D851&__ASYNCPOST=true&'
    suburb_raw = "WANTIRNA,3152"
    url_encode_suburb = urllib.parse.quote(suburb_raw)
    data_post = data_raw.format(url_encode_suburb)

    '''
    data_suburbs["prefixText"] = "wantirna"
    data_suburbs["count"] = "10"
    data_suburbs["contextKey"] = None
    '''
    response_content = requests.post(url_suburb_completion, data=data_post, headers=default_header)
    debug_print(response_content.text)
    debug_print(response_content.status_code)
    # key - school address; Value = ["school address", "postcode", "scores", "school type", "Enrollments", "link"]
    school_list = dict()
    rst_bs4 = BeautifulSoup(response_content.text, 'lxml')
    table_schools = rst_bs4.find('table', class_="table table-striped table-bordered table-hover")
    all_schools = table_schools.find_all('tr')
    for each_school in all_schools:
        if each_school["style"] == "color:White;background-color:#5D7B9D;font-weight:bold;":
            # skip first line
            continue
        else:
            school_properties = each_school.find_all('td')
            school_address_info = school_properties[0].find('a')
            school_real_link = better_education_base_url + school_address_info["href"]
            school_address = school_address_info.text.strip()
            debug_print(school_real_link)
            debug_print(school_address)

            school_score = school_properties[2].text.strip()
            debug_print(school_score)

            school_enrollment_num = school_properties[6].text.strip()
            debug_print(school_enrollment_num)

            school_type_info = school_properties[7].text.strip()
            debug_print(school_type_info)


def get_top_primary():
    default_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'bettereducation.com.au',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }
    url_top = "https://bettereducation.com.au/school/Primary/vic/vic_top_primary_schools.aspx"
    response_content = requests.get(url_top, headers=default_header)
    debug_print(response_content.text)
    debug_print(response_content.status_code)

# Main test
if __name__ == '__main__':
    #get_candidate_suburbs()
    #get_candidate_schools()
    get_top_primary()

