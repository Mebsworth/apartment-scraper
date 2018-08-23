import requests
from bs4 import BeautifulSoup as bs4
import time
import random

# INPUTS
MAX_RESULTS_PER_PAGE = 120 # Set by Craigslist
FILTER_BY_AVAILABILITY = True # Filter out apartments that are available now or before Sept 1.

def create_months():
	months_dict = {}
	months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
	for i in range(0,12):
		months_dict[months[i]] = i+1
	return months_dict

def get_text_from_html(html):
	return html.text.encode('utf-8').strip()

def get_availability(html):
	availability_html = html.find('span', attrs={'class': 'housing_movein_now property_date shared-line-bubble'})
	if (availability_html is not None):
		return get_text_from_html(availability_html)[10:]
	return ""

def get_address(html):
	address_html = html.find('div', attrs={'class':'mapaddress'})
	address = ""
	if (address_html is not None):
		address = get_text_from_html(address_html)
	return address

def get_num_bathrooms(html):
	bathrooms_html = html.find('span', attrs={'class': 'shared-line-bubble'})
	bathrooms = "0"
	if (bathrooms_html is not None):
		br_and_ba = bathrooms_html.find_all('b')
		if (len(br_and_ba) > 1):
			bathrooms = get_text_from_html(br_and_ba[1])
	return bathrooms

def get_apartment_full_page(link):
	rsp = requests.get(link)
	return bs4(rsp.text, 'html.parser')

def get_title(apt):
	return get_text_from_html(apt.find('a', attrs={'class': 'hdrlnk'}))

def get_price(apt):
	return get_text_from_html(apt.find('span', attrs={'class': 'result-price'}))

def get_info_about_space(apt):
	return apt.find('span', attrs={'class': 'housing'}).text.strip().split('\n')

def get_num_bedrooms(space_info):
	if (len(space_info) > 0):
		num_bedrooms = space_info[0].encode('utf-8').strip()
		num_bedrooms = num_bedrooms.split(" ")[0]
		return num_bedrooms
	return str(0)

def get_sqt_ft(space_info):
	if (len(space_info) > 1):
		sq_ft = space_info[1].encode('utf-8').strip()
		return sq_ft.split(" ")[0]
	return str(0)

def get_neighborhood(apt):
	neighborhood = apt.find('span', attrs={'class': 'result-hood'})
	if (neighborhood is not None): 
		neighborhood = neighborhood.text
		return neighborhood[2:-1].lower().encode('utf-8').strip()
	return str(0)

# Returns true if availability is September or later.
def filter_out_availability(availability):
	if (availability is not None) and (availability != ""):
		availability = availability.split(" ")
		num_month = months_dict[availability[0]]
		if num_month is None:
			print(availability[0])
		elif num_month < 9:
			return False
	return True

def parse_apartment(apt, existing_apartments, file):
	link = apt.find('a', attrs={'class': 'hdrlnk'})['href'].encode('utf-8').strip()
	if link not in existing_apartments:
		title = get_title(apt)
		price = get_price(apt)
		num_bedrooms = get_num_bedrooms(get_info_about_space(apt))
		sq_ft = get_sqt_ft(get_info_about_space(apt))
		neighborhood = get_neighborhood(apt)
		html = get_apartment_full_page(link)
		address = get_address(html)
		num_bathrooms = get_num_bathrooms(html)
		availability = get_availability(html)
		if filter_out_availability(availability):
			file.write(link + ', ' + title + ', ' + price + ', ' + num_bedrooms + ', ' + num_bathrooms + ', ' + availability + ', ' + sq_ft + ', ' + neighborhood + ',' + address + '\n')

def get_next_page(apts, url_base, params):
	time.sleep(random.randint(1,6))
	num_apts = len(apts)
	request_url = url_base + 's=' + str(num_apts) + '&' + params
	print(request_url)
	rsp = requests.get(request_url)
	html = bs4(rsp.text, 'html.parser')
	apts += html.find_all('li', attrs={'class':'result-row'})
	return apts

def search(url_base, params):
	rsp = requests.get(url_base + params)
	html = bs4(rsp.text, 'html.parser')
	apts = html.find_all('li', attrs={'class':'result-row'})
	num_apts = len(apts)

	while(num_apts % MAX_RESULTS_PER_PAGE == 0):
		apts = get_next_page(apts, url_base, params)
		num_apts = len(apts)
		print(num_apts)

	with open('apartments.txt', 'a') as file:
		for apt in apts: # for i in range(5)
			parse_apartment(apt, existing_apartments, file)


# Get existing apartments' links (identifiers) so we don't duplicate apartments.
existing_apartments = set()
with open('apartments.txt', 'w+') as file:
	existing_apartments = set([line.split(',')[0] for line in file.readlines()])
file.close()

# Do new search.
months_dict = create_months()
sfc_url_base = 'http://sfbay.craigslist.org/search/sfc/apa?'
# Neighborhoods: Mission, Potrero, Bernal.
sfc_params = 'nh=3&nh=18&nh=25&availabilityMode=0&laundry=1&laundry=4&max_bedrooms=2&max_price=4200&min_bathrooms=1&min_bedrooms=1'
search(sfc_url_base, sfc_params)








