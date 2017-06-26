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

"""
Define a specific parser for a website: 
It tries to find the correct tag depending on the arguments.
Multiples tags/classes/ids combinations can be provided in ordrer to search in DOM tree
Once found it returns it's first <a> child
"""
class Website_Parser():
	def __init__(self, tag_names, class_names=[], id_names=[]):
		self.tag_names = tag_names
		self.id_names = id_names
		self.class_names = class_names

	def parse(self, main_page_soup, site_url):
		article_top = main_page_soup

		for tag_name, id_name, class_name in itertools.zip_longest(self.tag_names, self.id_names, self.class_names):
			find_attributes={}
			if id_name is not None:
				find_attributes.update({"id":id_name})
			if class_name is not None:
				find_attributes.update({"class":class_name}) 

			article_top = article_top.find(tag_name, attrs=find_attributes)


		article_top_url = article_top.find("a")['href']

		if (article_top_url[:4] != "http" ):
			article_top_url = site_url+article_top_url

		return article_top_url


"""
Website_Fetcher: fetch data from listed website in 
main_exec and store the data to the db with fetch_main_article
"""
class Website_Fetcher():
	# Class variable :ie shared
	clientMongo = MongoClient('localhost', 27017)
	db = clientMongo.livefetch_test1
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

	def main_exec():
		websites = [
			# Press Payante
			Website_Fetcher( "Le Monde", "http://mobile.lemonde.fr", Website_Parser(["main"]) ),
			Website_Fetcher( "Le Figaro", "http://www.lefigaro.fr", Website_Parser(["section"]) ),
			Website_Fetcher( "Le Parisien", "http://m.leparisien.fr", Website_Parser(["article"]) ),
			Website_Fetcher( "Les Echos", "http://www.lesechos.fr", Website_Parser(["article"]) ),
			Website_Fetcher( "La Croix", "http://www.la-croix.com", Website_Parser(["div"], ["main-article"]) ),
			Website_Fetcher( "Liberation", "http://www.liberation.fr", Website_Parser(["article"]) ),
			Website_Fetcher( "L'Humanite", "http://www.humanite.fr", Website_Parser(["div","li"],[None,"first"], ["content",None]) ),		
			# Press Gratuite
			Website_Fetcher( "20 minutes", "http://www.20minutes.fr", Website_Parser(["article"]) ),
			Website_Fetcher( "CNews matin", "http://www.cnewsmatin.fr", Website_Parser(["div"], [None], ["main-content"]) ),
			# Pure player
			Website_Fetcher( "Mediapart", "http://www.mediapart.fr", Website_Parser(["div","h3"], ["une-block", "title" ]) ),
			# tf1 WTFFFFF
			Website_Fetcher( "BFMTV", "http://www.bfmtv.com", Website_Parser(["article"]) ),
			Website_Fetcher( "LCI", "http://www.lci.fr", Website_Parser(["div"],["article-xl-block-topic"]) ),
			Website_Fetcher( "France Info", "http://www.francetvinfo.fr", Website_Parser(["article"]) ),
			Website_Fetcher( "Rue 89", "http://www.rue89.com", Website_Parser(["article"]) ),
			# http://www.agoravox.fr/?page=home14_unes --Website_Fetcher( "Agoravox", "http://www.agoravox.fr", Website_Parser(["div"],[None],["unes"]) ),
			
			# atlantico
			Website_Fetcher( "Atlantico", "http://www.atlantico.fr", Website_Parser(["div"],[],["cover"]) ),
			
		]

		for website in websites:
			try:
				website.fetch_main_article()
			except Exception as e:
				print("Problem with " + website.newspaper_name)
				print (str(e))


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
	size_folder = 'x'.join(map(str, Website_Fetcher.thumbnail_size))
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
			im.thumbnail(Website_Fetcher.thumbnail_size)
			im.save(outfile, "PNG")
		except IOError:
			print("cannot create thumbnail for " + infile + "=>" + outfile)


# Useful if your deleted your local image_db
def fecth_images_from_db_and_create_thumbnail():
	articles = Website_Fetcher.articles_collection.find({})
	for article in articles:
		fetch_image( article["top_image"] )
		create_thumbnail( article["top_image"] )


def add_local_path():
	print("Adding local path: START")
	articles = Website_Fetcher.articles_collection.find({})
	for article in articles:
		result = Website_Fetcher.articles_collection.update_one( {"_id": article["_id"]}, {'$set':{"local_top_image": get_imagedb_local_path(article["top_image"])}})
	print("Adding local path: END")


def add_local_thumbnails():
	print("Adding local thumbnail path: START")
	articles = Website_Fetcher.articles_collection.find({})
	for article in articles:
		result = Website_Fetcher.articles_collection.update_one( {"_id": article["_id"]}, {'$set':{"local_thumbnail": get_imagedb_local_thumbnail_path(article["top_image"])}})
	print("Adding local thumbnail path: END")

def remove_static_from_db():
	add_local_path()
	add_local_thumbnails()

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
	Website_Fetcher.main_exec()