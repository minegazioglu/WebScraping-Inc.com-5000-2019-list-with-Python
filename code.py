import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import string
import re

url = "https://www.inc.com/inc5000/2019/top-private-companies-2019-inc5000.html"
r = requests.get(url)
soup = BeautifulSoup(r.content,"html.parser")
detail = str(soup)
start = detail.find("companylist")+13
end = detail.find("buyerzonewidgets",start)-18
all_info = detail[start:end]

import json

data = json.loads(all_info)

data_framed = pd.DataFrame(data)

data_framed.columns = ['id',
                       'company_name',
                       'weblink_suffix',
                       'industry',
                       'state',
                       'city',
                       'metro',
                       'years_on_list',
                       'rank',
                       'revenue',
                       'raw_revenue',
                       'growth']

data_framed = data_framed.drop([1593])

weblink_suffix = data_framed["weblink_suffix"]
weblinks = []

for suffix in weblink_suffix:
    suffix = "https://www.inc.com/profile/" + suffix
    weblinks.append(suffix)

#html_title_list = []
#
#for weblink in weblinks:
#    page = requests.get(weblink)
#    html = BeautifulSoup(page.text,"html.parser")
#    if html.title.string == None:
#        html_title_list.append(weblink)
#print(html_title_list)

company_list = []
leadership_list = []
revenue_list = []
three_year_growth_list = []
industry_list = []
city_list = []
state_list = []
founded_list = []
employees_list = []
website_list = []

for i,link in enumerate(weblinks):

    r = requests.get(link)
    soup = BeautifulSoup(r.text,"html.parser")
    detail = str(soup)

    # Leadership
    start = detail.find("Leadership")
    start = detail.find("<span>",start)+6
    end = detail.find("</span>",start)
    leadership = detail[start:end]
    if len(leadership)<300:
        leadership_list.append(leadership.replace("<!-- -->", ""))
    elif len(leadership)>300:
        leadership = soup.find('dl', attrs={'class':'companyProfiles__rank__1qsr3 col-12'})
        if leadership !=  None:
            leadership = leadership.text
            leadership_list.append(leadership)
        else:
            leadership = "None Found"
            leadership_list.append(leadership)

    # 2018 Revenue

    start = detail.find("Revenue",end)
    start = detail.find("-->",start)+3
    end= detail.find("</dd>",start)
    revenue = detail[start:end]
    if not revenue[0].isdigit():
        revenue = data_framed["revenue"][i]
    revenue_list.append(revenue)

    # 3-Year Growth

    start = detail.find("3-Year Growth",end)
    start = detail.find("</dt>",start)+9
    end= detail.find("<!--",start)
    three_year_growth = detail[start:end]
    three_year_growth = (str(three_year_growth) + "%")
    if not three_year_growth[0].isdigit():
        three_year_growth = str(data_framed["growth"][i]) + "%"
    three_year_growth_list.append(three_year_growth)

    # Industry

    start = detail.find("Industry",end)
    start = detail.find('<dd class="profileCss.singleIndustry">',start)+38
    end= detail.find("</dd>",start)
    industry = detail[start:end]
    if len(industry)>300:
        industry = data_framed["industry"][i]
    industry_list.append(industry.replace("&amp;","&"))

    # Location

    start = detail.find("Location",end)
    city_start = detail.find('<dd>',start)+4
    city_end= detail.find("<!--",start)
    state_start = detail.find('<!-- -->',start)+18
    state_end = detail.find('<!-- -->',start)+20
    city = detail[city_start:city_end]
    state = detail[state_start:state_end]
    letter_list = list(string.ascii_uppercase)
    if state[0] not in letter_list:
        state = data_framed["state"][i]
    if len(city)>300:
        city = data_framed["city"][i]
    city_list.append(city)
    state_list.append(state)

    # Founded

    start = detail.find("Founded",state_end)
    start = detail.find('<dd>',start)+4
    end= detail.find("</dd>",start)
    founded = detail[start:end]
    if len(founded) == 4:
        founded_list.append(founded)
    else:
        founded = "Problem"
        founded_list.append(founded)
    
    # Number of Employees

    start = detail.find("Employees",state_end)
    start = detail.find('<dd>',start)+4
    end= detail.find("</dd>",start)
    employees = detail[start:end]
    if len(employees)<6:
        employees_list.append(employees)
    else:
        employees = "None Found"
        employees_list.append(employees)
    
    # Website

    start = detail.find("Website",state_end)
    start = detail.find('<a href=',start)+9
    end= detail.find("target",start)-28
    website = detail[start:end]
    if website.startswith("http") & len(website)<100:
        website_list.append(website)
    else:
        start = detail.find("Website")
        start = detail.find('<a href=',start)+9
        end= detail.find("target",start)+21
        website = detail[start:end]
        website = re.sub(r'(?is)".+', '', website)
        if website.startswith("http") & len(website)<100:
            website_list.append(website)
        else:
            website = "Problem"
   
company_name = data_framed.company_name.tolist()

length_list = {"Leadership":len(leadership_list),
              "Revenue":len(revenue_list),
              "Three":len(three_year_growth_list),
              "Industry":len(industry_list),
              "City":len(city_list),
              "State":len(state_list),
              "Founded":len(founded_list),
              "Employees":len(employees_list),
              "Website":len(website_list)}

inc_dataframe = pd.DataFrame(list(zip(company_name,leadership_list, revenue_list, 
                                      three_year_growth_list,industry_list,
                                      city_list,state_list,founded_list,
                                      employees_list,website_list,weblinks)),
                            columns=["Company Name",'Leadership','2018-Revenue', 
                                     '3 Year Growth',"Industry","City","State","Founded",
                                     "Number of Employees","Website","Inc_com_Websites"])
   
inc_dataframe.to_csv("researching_40.csv")




##
