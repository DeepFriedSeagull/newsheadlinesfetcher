
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
from PIL import Image


class Soup_Parser():
	def __init__(self, tag_names, class_names=[], id_names=[]):
		self.tag_names = tag_names
		self.id_names = id_names
		self.class_names = class_names

	def parse(self, main_page_soup, site_url):
		article_top = main_page_soup

		for tag_name, id_name, class_name in itertools.zip_longest(self.tag_names, self.id_names, self.class_names):
			# print (tag_name, id_name, class_name)
			# print( article_top )


			# if ( id_name and class_name):
			# 	article_top = article_top.find(tag_name, id=id_name, class_=class_name)
			# elif (id_name):
			# 	article_top = article_top.find(tag_name, id=id_name)
			# elif (class_name):	
			# 	article_top = article_top.find(tag_name, class_=class_name)
			# else:
			# 	article_top = article_top.find(tag_name)

			find_attributes={}
			if id_name is not None:
				find_attributes.update({"id":id_name})
			if class_name is not None:
				find_attributes.update({"class":class_name}) 

			article_top = article_top.find(tag_name, attrs=find_attributes)

			# print( "done" )
			# print( article_top )
			# print( "done2" )

		article_top_url = article_top.find("a")['href']

		if (article_top_url[:4] != "http" ):
			article_top_url = site_url+article_top_url

		return article_top_url

class Website():
	# Class variable :ie shared
	clientMongo = MongoClient('localhost', 27017)
	db = clientMongo.livefetch
	images_collection = db.imagesCollection
	articles_collection = db.articlesCollection
	newspapers_collection = db.newspapersCollection
	thumbnail_size = (150, 150)

	def __init__(self, newspaper_name, site_url, parser ):
		self.newspaper_name = newspaper_name
		self.site_url = site_url
		self.parser = parser
		# adding newspaper if not found in db
		if (self.newspapers_collection.find_one({"name":newspaper_name}) is None):
			self.newspapers_collection.insert_one({"name":newspaper_name, "url":site_url})

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
				# "images": article.images,
				"top_image" : article.top_image,
				"local_top_image" : get_imagedb_local_path(article.top_image),
				"local_thumbnail" : get_imagedb_local_thumbnail_path(article.top_image),
				# "date_of_publication" :,
				"time_of_insert_iso" : datetime.datetime.now().isoformat(),
				"TOI" : datetime.datetime.utcnow(),
				"summary": article.summary,
				"tags" : article.keywords
			})

			print("Adding and Fetching: " + article.title)
			self.articles_collection.insert_one(newArticle)

			fetch_image ( article.top_image )
			create_thumbnail ( article.top_image )

		else:
			# print("Article already in the db: " + exist_article["title"])
			pass


# Max length of file is 256 on windows
# Taking some marge limiting on 240
def truncated_basename( remote_path ):

	basename = os.path.basename( urlparse(remote_path).path )
	filename =  os.path.splitext( basename )[0]
	extension = os.path.splitext( basename)[1]

	dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"static")
	full_path = os.path.join( dir_path, basename)

	if ( len(full_path)  > 240 ):
		idx_max = 240 - len(dir_path) - len(extension)
		result_name = filename[:idx_max] + extension
		return result_name
	return basename


def get_imagedb_local_path( remote_path ):
	image_local_path = truncated_basename(remote_path)
	image_local_path = os.path.join( "images_db", image_local_path)
	return image_local_path


def get_imagedb_local_thumbnail_path( remote_path ):
	thumbnail_path = os.path.splitext( os.path.basename( urlparse(truncated_basename(remote_path)).path ))[0]+ ".png"
	size_folder = 'x'.join(map(str, Website.thumbnail_size))
	destination_folder = os.path.join( "images_db", size_folder )
	thumbnail_path = os.path.join(destination_folder, thumbnail_path)
	return thumbnail_path


def fetch_image( remote_path ):
	image_local_path = get_imagedb_local_path(remote_path)
	image_local_path = os.path.join( "newsheadlinesfetcher", "static", image_local_path)

	print(" Fetching: " + remote_path +" To: "+image_local_path)
	if (not os.path.isfile(image_local_path)):
		r = requests.get(remote_path, stream=True)
		if r.status_code == 200:
			with open(image_local_path, 'wb') as f:
				for chunk in r:
					f.write(chunk)
			print( "File correctly downloaded ")
	else:
		print("File already downloaded")
		pass


def create_thumbnail(remote_path):
	infile = os.path.join( "newsheadlinesfetcher", "static", get_imagedb_local_path(remote_path))
	outfile = os.path.join( "newsheadlinesfetcher", "static", get_imagedb_local_thumbnail_path(remote_path))
	if (not os.path.isfile(outfile) ):
		try:
			im = Image.open(infile)
			im.thumbnail(Website.thumbnail_size)
			im.save(outfile, "PNG")
		except IOError:
			print("cannot create thumbnail for " + infile + "=>" + outfile)


# Useful if your deleted your local image_db
def fecth_images_from_db_and_create_thumbnail():
	articles = Website.articles_collection.find({})
	for article in articles:
		fetch_image( article["top_image"] )
		create_thumbnail( article["top_image"] )


def add_local_path():
	print("Adding local path: START")
	articles = Website.articles_collection.find({})
	for article in articles:
		result = Website.articles_collection.update_one( {"_id": article["_id"]}, {'$set':{"local_top_image": get_imagedb_local_path(article["top_image"])}})
	print("Adding local path: END")

def add_local_thumbnails():
	print("Adding local thumbnail path: START")
	articles = Website.articles_collection.find({})
	for article in articles:
		result = Website.articles_collection.update_one( {"_id": article["_id"]}, {'$set':{"local_thumbnail": get_imagedb_local_thumbnail_path(article["top_image"])}})
	print("Adding local thumbnail path: END")


def remove_static_from_db():
	add_local_path()
	add_local_thumbnails()

def main_exec():
	websites = [
		# Press Payante
		Website( "Le Monde", "http://mobile.lemonde.fr", Soup_Parser(["main"]) ),
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


def create_thumbnails(size):
	origin_folder = os.path.join("static", "images_db")

	in_files = [f for f in os.listdir(origin_folder) if os.path.isfile(os.path.join(origin_folder, f))]

	size_folder = 'x'.join(map(str, size))
	destination_folder = os.path.join( "static", "images_db", size_folder )

	#if folder doesn't exist, create it
	if (os.path.isdir(destination_folder) is False):
		print( "Creating: " + destination_folder)
		os.makedirs( destination_folder )

	for infile in in_files:
		infile = os.path.join(origin_folder, infile)
		outfile = os.path.join(destination_folder, os.path.splitext(os.path.basename(infile))[0]+ ".png")

		if infile != outfile:
			try:
				im = Image.open(infile)
				im.thumbnail(size)
				im.save(outfile, "PNG")
			except IOError:
				print("cannot create thumbnail for", infile)

def create_thumbnails_150():
	create_thumbnails((150,150))

def create_thumbnails_120():
	create_thumbnails((120,120))

if __name__ == "__main__":
	fecth_images_from_db_and_create_thumbnail()