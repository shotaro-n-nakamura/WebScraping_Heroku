import pandas as pd
import requests
from bs4 import BeautifulSoup

# url template for constructing the page url
URL_TEMPLATE = 'https://www.pakwheels.com/used-cars/search/-/mk_{}/md_{}/?page={}'
# read the input csv containing vehicles to search for
searchCsv = pd.read_csv ('pop.csv')
# create an array for storing the results
results = []
# iterate over the input csv row-by-row
for row in searchCsv.itertuples ():
    # extract make and model from the row
    make = row.Make
    model = row.Model
    # iterate over the result pages
    # change the parameters below to configure how many pages you want
    for pageNum in range (1, 2):
        print ("\rCollecting results for {} {} (Page {})... ".format (make, model, pageNum), end='')
        # construct the page url
        url = URL_TEMPLATE.format (make, model, pageNum)
        # request the page html
        r = requests.get (url)
        # soupify the response html
        soup = BeautifulSoup (r.text, 'html.parser')
        # select all listings from the results
        listings = soup.find_all ('li', attrs={'class': 'classified-listing'})

        # extract required info from each listing
        for rank, listing in enumerate (listings):
            # extract the listing href by looking for the <a> tag that has 'car-name' class
            href = listing.find ('a', attrs={'class': 'car-name'})['href']

            # extract the listing last_updated by looking for the 'div' that has 'dated' class
            last_updated = listing.find ('div', attrs={'class': 'dated'}).text.strip ()
            price = listing.find ('div', attrs={'class': 'price-details'}).text.strip ()
            ul = listing.find ('ul', attrs={'class': 'search-vehicle-info-2'})
            year, mileage, type, cc, transmission = ul.find_all ('li')[:5]
            year, mileage, type, cc, transmission = year.text, mileage.text, type.text, cc.text, transmission.text

            # extract the city by looking for the 'div' tag that has 'row' class
            # and then extracting the first <li> from the first <ul> inside it
            city = listing.find ('div', attrs={'class': 'row'}).ul.li.text

            # remove 'leased' from the city
            city = city.replace ("Leased", "").strip ()

            # create result dictionary to store the data
            result = {
                'make': make,
                'model': model,
                'url': 'https://www.pakwheels.com{}'.format (href),
                'last_updated': last_updated,
                'city': city,
                'price': price,
                'year': year,
                'mileage': mileage,
                'type': type,
                'cc': cc,
                'transmission': transmission,
                'page num': pageNum,
                'rank': rank + 1,
                'featured': 'featured-ribbon' in str (listing)
            }

            # add dictionary to results array
            results.append (result)

    print ('done!')

# write results to csv
pd.DataFrame (results).to_csv ('results.csv', index=False)
