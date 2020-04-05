# LightSpider-AUProperty
Simple spider for real estate (domain) only for study purpose.

By Forrest Xiong.
Email: forrestisagoodman@gmail.com
wechat: ARealGoodGuy

# prerequisite
Supports python 3.7+
Install required python module:
pip3 install -r requirements.txt


# V1.0  - [Released in 2020.04.05]
1. Only supports realestate "https://www.realestate.com.au/"
2. Configuration file - Customized Query - "AUPropertySpider.yaml"
2.1 Search parameters:
<buy, rent, sold, share, New homes, Find agents, Lifestyle, News, Commercial>

source_type: "buy"

< house, apartment, townhouse>

property_type: "house"

< nsw, qld, sa, tas, vic, wa>

< support only one value>

< could be empty>
state_name: "vic"

< suburb name: croydon, werribee,...>

< City name Sydney,  Melbourne, Brisbane, Perth, Adelaide, Gold Coast, Canberra, Newcastle, Wollongong, Logan City.>

< support two or more values>

location_list:
             #- "coydon"
             - "werribee"
             #- "ringwood"
             
< suggested to be from 1 to 5 or "any">

< max_bed must be larger than min_bed>
min_bed: "1"

max_bed: "any"

< suggested to be from 1 to 5 or "any">
min_bath: "1"

< 100000 ($)>
min_price: "any"

< 1000000 ($)>
max_price: "any"
< 300 (m2)>
min_land_size: "any"

< ignored by realestate but domain>
max_land_size: "any"


2.2 RequestHeaders
Suggested to copy the cookie from Chrome DevTools

2.3 RequestTimeInterval
Determine how frequent to send out the requests, just in case the target web server detect the spider bot behavior.
