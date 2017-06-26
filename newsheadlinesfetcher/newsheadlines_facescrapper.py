from bs4 import BeautifulSoup
import requests
import re
from urllib.request import urlopen, Request
import os
# import cookielib
import json


class FaceScrapper():

	def get_soup(url,header):
		return BeautifulSoup( urlopen( Request(url,headers=header)),'html.parser')


	ROOT_DIR="reference_images"

	header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

	queries=[ 
		'emmanuel+macron',
		'benoit+hamon',
		'nathalie+arthaud',
		'philippe+poutou',
		'jacques+cheminade' 
		'jean+lassalle',
		'jean+luc+melenchon',
		'francois+asselineau',
		'marine+le+pen',
		'nicolas+dupont+aignan',
		'francois+fillon'
		]


	def main_exec():	
		for query in queries:
			real_query=query+'+visage'
			url="https://www.google.co.in/search?q="+real_query+"&source=lnms&tbm=isch"
			soup = get_soup(url,header)

			ActualImages=[] # contains the link for Large original images, type of  image
			for a in soup.find_all("div",{"class":"rg_meta"}):
				link , Type =json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
				ActualImages.append((link,Type))

			print  ("there are total" , len(ActualImages),"images for " + query)

			if not os.path.exists(ROOT_DIR):
						os.mkdir(ROOT_DIR)
			
			candidate_name = ('_').( query.split('+') )

			DIR = os.path.join(ROOT_DIR, candidate_name )

			if not os.path.exists(DIR):
						os.mkdir(DIR)

			counter = 0
			for i , (img , Type) in enumerate( ActualImages):
				try:
					if len(Type)==0:
						output_file = os.path.join(DIR, "{}_{num:02d}.jpg".format(candidate_name,num=counter))
					else :
						output_file = os.path.join(DIR, "{}_{num:02d}.{type}".format(candidate_name,num=counter,type=Type))

					print( img )

					r = requests.get(img) #, stream=True)
					if r.status_code == 200:
						with open(output_file, 'wb') as f:
							for chunk in r:
								f.write(chunk)

					counter = counter + 1
					
				except Exception as e:
					print ("could not load : "+img)
					print (e)



if __name__ == '__main__':
	FaceScrapper.test_exec()
