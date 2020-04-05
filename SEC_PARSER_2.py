from bs4 import BeautifulSoup
import requests
import sys



# Choose which financial metrics to pull from 10-k
file = open('us-gaap_schemas.txt')

metrics = file.read().split("\n")

# Access page
companies = {"ROIC" : '0001407623'}
# = {"SBUX": "829224", "AAPL": "320193", "BA": "12927", "Googl": "0001652044"}
filing_year = 2019
type = '10-k'
dateb = '20201231'

base_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type={}&dateb={}"

for company in companies:
    company_metrics = set([])
    edgar_resp = requests.get(base_url.format(companies[company], type, dateb))
    edgar_str = edgar_resp.text

    # Find the document link
    doc_link = ''
    soup = BeautifulSoup(edgar_str, 'html.parser')
    table_tag = soup.find('table', class_='tableFile2')
    rows = table_tag.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 3:
            if str(filing_year) in cells[3].text:
                doc_link = 'https://sec.gov' + cells[1].a['href']

    # Exit if document link couldn't be found
    if doc_link == '':
        print("Couldn't find the document link")
        sys.exit()

    # Obtain HTML for document page
    doc_resp = requests.get(doc_link)
    doc_str = doc_resp.text

    # Find the XBRL link
    xbrl_link = ''
    soup = BeautifulSoup(doc_str, 'html.parser')
    table_tag = soup.find('table', class_='tableFile', summary='Data Files')
    rows = table_tag.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 3:
            if "INS" in str(cells[3]) or "INSTANCE" in str(cells[1]):
                xbrl_link = 'https://www.sec.gov' + cells[2].a['href']



    # Obtain XBRL text from document
    xbrl_resp = requests.get(xbrl_link)
    xbrl_str = xbrl_resp.text

    # Find and print stockholder's equity
    soup = BeautifulSoup(xbrl_str, 'lxml')
    tag_list = soup.find_all()

    # Find and print stockholder's equity
    print(list(companies.keys())[list(companies.keys()).index(company)]+" "+
          str(filing_year))
    print('--------------------')
    print("(In Millions)")
    for tag in tag_list:
        for metric in metrics:
            if tag.name == 'us-gaap:{0}'.format(metric):
                if ("FD"+str(filing_year)+"Q4YTD") == str(tag.attrs['contextref']) or ("FI"+str(filing_year)+"Q4") == str(tag.attrs['contextref']):
                #print(metric)
                #print(str(("FD"+str(filing_year)+"Q4YTD")))
                #print(str(filing_year-1))
                #print(str(tag.attrs))
                #print(str(filing_year) in str(tag.attrs['contextref']))
                    try:
                        company_metrics.add("{0} {1}: $ {2:,.2f}".format(str(filing_year), metric, float(tag.text)/1000))
                    except ValueError:
                        company_metrics.add("{0} {1}:{2}".format(str(filing_year), metric, tag.text))
                    #print("{0} {1}: $ {2:,.2f}".format(str(filing_year), metric, float(tag.text)/1000))


    for metric in company_metrics:
        print(metric)

    print('\n')