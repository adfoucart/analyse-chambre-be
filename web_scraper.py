'''
Récupère les version HTML des comptes-rendus de lachambre.be

Auteur: Adrien Foucart

usage: python web_scraper.py
'''

from urllib import request
from urllib.error import HTTPError
import os

PATH_OUT = './archives/'

def scrape(leg):
	i = 0
	while(True):
		i += 1
		url = "http://www.lachambre.be/doc/PCRI/html/%02d/ip%03dx.html"%(leg, i)
		try:
			f = request.urlopen(url)
		except HTTPError:
			break
		if( f.getcode() != 200 ): break
		html = f.read()
		with open(os.path.join(PATH_OUT, "%02d_%03d.html"%(leg,i)), 'wb') as fp:
			fp.write(html)

# Récupère la 54ème législature
scrape(54)