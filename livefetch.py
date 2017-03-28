
import requests
import newspaper
import pymongo
import datetime
import os
import itertools

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from newspaper import Article
from pymongo import MongoClient


class Soup_Parser():


	def __init__(self, tag_names, class_names=[], id_names=[]):
		self.tag_names = tag_names
		self.id_names = id_names
		self.class_names = class_names

	def parse(self, main_page_soup, site_url):
		arcticle_top = main_page_soup

		for tag_name, id_name, class_name in itertools.zip_longest(self.tag_names, self.id_names, self.class_names):
			# print (tag_name, id_name, class_name)
			# print( arcticle_top )


			# if ( id_name and class_name):
			# 	arcticle_top = arcticle_top.find(tag_name, id=id_name, class_=class_name)
			# elif (id_name):
			# 	arcticle_top = arcticle_top.find(tag_name, id=id_name)
			# elif (class_name):	
			# 	arcticle_top = arcticle_top.find(tag_name, class_=class_name)
			# else:
			# 	arcticle_top = arcticle_top.find(tag_name)

			find_attributes={}
			if id_name is not None:
				find_attributes.update({"id":id_name})
			if class_name is not None:
				find_attributes.update({"class":class_name}) 

			arcticle_top = arcticle_top.find(tag_name, attrs=find_attributes)

			# print( "done" )
			# print( arcticle_top )
			# print( "done2" )

		arcticle_top_url = arcticle_top.find("a")['href']

		if (arcticle_top_url[:4] != "http" ):
			arcticle_top_url = site_url+arcticle_top_url

		return   arcticle_top_url


class Website():

	# Class variable :ie shared
	clientMongo = MongoClient('localhost', 27017)
	db = clientMongo.livefetch
	images_collection = db.imagesCollection
	articles_collection = db.articlesCollection

	def __init__(self, newspaper_name, site_url, parser ):
		self.newspaper_name = newspaper_name
		self.site_url = site_url
		self.parser = parser

	def fetch_main_article(self):
		print ("Fetching: ", self.newspaper_name)
		main_page = requests.get(self.site_url)
		main_page_soup = BeautifulSoup(main_page.text, "html.parser")
		
		article_url = self.parser.parse( main_page_soup, self.site_url)
		# print (article_url)
		article = Article(article_url,language="fr")
		article.download()
		article.parse()
		article.nlp()


		newArticle = {
			"origin": self.newspaper_name,
			"url": article_url
		}

		exist_article = self.articles_collection.find_one({"url": article_url})

		if (exist_article is None):
			newArticle.update( {
				"text" : article.text,
				"authors" : article.authors,
				"title": article.title,
				# "images": arcticle.images,
				"top_image" : article.top_image,
				# "date_of_publication" :,
				"time_of_insert_iso" : datetime.datetime.now().isoformat(),
				"summary": article.summary,
				"tags" : article.keywords
			})

			print("Adding and Fetching: " + article.title)
			self.articles_collection.insert_one(newArticle)
			fetch_image ( article.top_image )
		else:
			# print("Article already in the db: " + exist_article["title"])
			pass

def fetch_image( remote_path):
	image_local_path = os.path.basename( urlparse(remote_path).path )
	image_local_path = os.path.join("images_db", image_local_path)
	image_local_path = os.path.join("static", image_local_path)
	if (not os.path.isfile(image_local_path)):
		r = requests.get(remote_path, stream=True)
		if r.status_code == 200:
			with open(image_local_path, 'wb') as f:
				for chunk in r:
					f.write(chunk)
			# print( "File correctly downloaded ")
	else:
		# print("File already downloaded")
		pass

def fecth_images_from_db():
	articles = Website.articles_collection.find({})
	for article in articles:
		fetch_image( article["top_image"] )

def add_local_path():
	print("Adding local path: START")
	articles = Website.articles_collection.find({})
	for  article in articles:
		image_local_path = os.path.basename( urlparse(article["top_image"]).path )
		image_local_path = os.path.join("images_db", image_local_path)
		image_local_path = os.path.join("static", image_local_path)
		result = Website.articles_collection.update_one( {"_id": article["_id"]}, {'$set':{"local_top_image":image_local_path}})
	print("Adding local path: END")

def main_exec():
	websites = [
		# Press Payante
		Website( "Le Monde", "http://mobile.lemonde.fr", Soup_Parser(["article"], ["une"]) ),
		Website( "Le Figaro", "http://www.lefigaro.fr", Soup_Parser(["section"]) ),
		Website( "Le Parisien", "http://m.leparisien.fr", Soup_Parser(["article"]) ),
		Website( "Les Echos", "http://www.lesechos.fr", Soup_Parser(["article"]) ),
		Website( "La Croix", "http://www.la-croix.com", Soup_Parser(["div"], ["main-article"]) ),
		Website( "Liberation", "http://www.liberation.fr", Soup_Parser(["article"]) ),
		Website( "L'Humanite", "http://www.humanite.fr", Soup_Parser(["div","li"],[None,"first"], ["content",None]) ),		
		# Press Gratuite
		Website( "20 minutes", "http://www.20minutes.fr", Soup_Parser(["article"]) ),
		Website( "CNews matin", "http://www.cnewsmatin.fr", Soup_Parser(["div"], [None], ["main-content"]) ),
		# Pure player
		Website( "Mediapart", "http://www.mediapart.fr", Soup_Parser(["div","h3"], ["une-block", "title" ]) ),
		# tf1 WTFFFFF
		Website( "BFMTV", "http://www.bfmtv.com", Soup_Parser(["article"]) ),
		Website( "LCI", "http://www.lci.fr", Soup_Parser(["div"],["article-xl-block-topic"]) ),
		Website( "France Info", "http://www.francetvinfo.fr", Soup_Parser(["article"]) ),
		Website( "Rue 89", "http://www.rue89.com", Soup_Parser(["article"]) ),
		# http://www.agoravox.fr/?page=home14_unes --Website( "Agoravox", "http://www.agoravox.fr", Soup_Parser(["div"],[None],["unes"]) ),
		
		# atlantico
		Website( "Atlantico", "http://www.atlantico.fr", Soup_Parser(["div"],[],["cover"]) ),
		
	]

	for website in websites:
		try:
			website.fetch_main_article()
		except Exception as e:
			print("Problem with " + website.newspaper_name)
			print (str(e))


if __name__ == "__main__":
	add_local_path()