#!/usr/bin/env python
from wordcloud import WordCloud
from pymongo import MongoClient
import os
from stop_words import get_stop_words
import unicodedata
from collections import Counter
import string
import codecs


class CloudGenerator():
	mongo_client = MongoClient()
	db = mongo_client.livefetch
	local_stop_words = set()

	with codecs.open(os.path.join(os.path.dirname(__file__), 'data','stop_words.txt'),'r',encoding='utf8') as f:
		file_content = f.read()
		local_stop_words = set([x.strip() for x in file_content.split('\n')])

	# Generate a word cloud image
	def generate_image_cloud(array_titles):
		#removing ponctuation
		text = ' '.join(array_titles)
		punctuation_to_remove = string.punctuation.translate(str.maketrans('', '','\''))
		text = text.translate(str.maketrans("", "", punctuation_to_remove))

		# Getting stop words
		stop_words = get_stop_words('french')
		stop_words = set( stop_words )
		stop_words |= CloudGenerator.local_stop_words
		stop_words = [normalize_caseless(word) for word in stop_words]


		# Other way to get the most frequent words
		most_common_words = Counter(text.split()).most_common()
		most_common_words = [ word[0] for word in most_common_words if word[1] > 5 and word[0] not in stop_words]
		print(most_common_words)

		# Using wordcloud
		wordcloud = WordCloud(stopwords=stop_words,
			background_color="white", max_words=200, width=600, height=400).generate(text)

		image = wordcloud.to_image()
		image_path = os.path.join("static", "img","wordcloud.png")
		image.save( image_path , format='png')


def normalize_caseless(text):
	return unicodedata.normalize("NFKC", text.casefold())

def filter_title_by_candidates(title):
	candidats=['dupont','aignan','pen','macron','hamon','arthaud','poutou',
	'cheminade','lassalle', 'mélenchon','asselineau', 'fillon']
	for candidat in candidats:
		if candidat in title:
			return True
	return False

def fetch_filtered_titles_from_db():
	titles_list = list( CloudGenerator.db.articlesCollection.find({}, { "_id":0, "title":1 } ) )
	str_titles = [normalize_caseless(title_dic["title"]) for title_dic in titles_list if "title" in title_dic]
	str_titles = list( filter( filter_title_by_candidates, str_titles) )
	return str_titles

if __name__ == '__main__':
	CloudGenerator.generate_image_cloud( fetch_filtered_titles_from_db() )