import requests
from bs4 import BeautifulSoup

"""
	Author : Kshitij Burman <kburman6@gmail.com>

"""

class IMDBParser:
	def __init__(self):
		pass

	def parseMovie(self,id):
		item = {"_id":id}
		persons = {}
		url = 'http://www.imdb.com/title/'+id+'/'
		r = requests.get(url)
		
		if r.ok :
			soup = BeautifulSoup(r.text,'html5lib')
			self.soup = soup
			# overview table
			ov = soup.find(attrs={"id":"title-overview-widget-layout"})
			ov = ov.tbody

			# check if cover image exists or not
			img_primary = ov.find('td',attrs={"id":"img_primary"})
			if img_primary.div != None:
				img_primary = img_primary.find('img',attrs={"itemprop":"image"})['src']
			del img_primary

			# overview top
			ovt = ov.find('td',attrs={"id":"overview-top"})
			# get header
			header = ovt.find(attrs={"class":"header"})
			# get name 
			item['name'] = header.find(attrs={"class":"itemprop","itemprop":"name"}).text
			item['name'] = self.shave(item['name'])

			# get year
			item['relase_year'] = header.find('a').text
			del header

			# get info bar
			infobar = ovt.find(attrs={"class":"infobar"})

			# get content rating
			content_rating = infobar.find(attrs={"itemprop":"contentrating"})
			if content_rating != None:
				item['content_rating'] = content_rating['content']
			del content_rating

			# get time
			time = infobar.find(attrs={"itemprop":"duratin"})
			if time != None:
				item['time'] = self.shave(time.text)

			del infobar
			# get rating
			rating = ovt.find(attrs={"class":["star-box","giga-star"]}) 
			rating = rating.find(attrs={"class":"star-box-details","itemprop":"aggregateRating"})

			# there may be review there not present 
			# so check for it
			rate = rating.find(attrs={"itemprop":"ratingValue"})
			if rate != None:
				item['ratings '] = self.shave(rate.text)
			del rate

			ratecount = rating.find(attrs={"itemprop":"ratingCount"})
			if ratecount != None:
				item['rating_users'] = self.shave(ratecount.text)
			del rating

			# get summary of the movie
			desc = ovt.find(attrs={"itemprop":"description"})
			if desc != None:
				item['desc'] = self.shave(desc.text)
			del desc
			
			humans = ovt.find(attrs={"itemprop":"creator"})
			human_list = []
			if 'writers' in item:
				human_list = mov['writers']
			for i in humans.findChildren('a',attrs={"itemprop":"url"}):
				uid,name = self.createPerson(i)
				persons[uid]={"name":name}
				if uid not in human_list:
					human_list.append(uid)
				
			item['writers'] = human_list
			del human_list
			del humans
			del i
			
			
			humans = ovt.find(attrs={"itemprop":"director"})
			human_list = []
			if 'director' in item:
				human_list = mov['director']
			for i in humans.findChildren('a',attrs={"itemprop":"url"}):
				uid,name = self.createPerson(i)
				persons[uid]={"name":name}
				if uid not in human_list:
					human_list.append(uid)
				
			item['director'] = human_list
			del human_list
			del humans
			del i
			
			del ovt
			del ov
			
			# now get cast people
			cast_list = soup.find('table',attrs={"class":"cast_list"})
			cast_list = cast_list.tbody
			cast_people = {}
			for a in cast_list.findChildren('tr'):
				if 'class' in  a.attrs:
					profile = {}
					# thumb pic
					img = a.find(attrs={"class":"primary_photo"}).a.img
					src = img['src']
					if 'loadlate' in img.attrs:
						src = img['loadlate']
					del img
					if '/nopicture/' not in src:
						profile['picture_small'] = src
					
					# get name				
					profile['name'] = self.shave(a.find(attrs={"itemprop":"name"}).text)
					# get IMDB ID
					uid = a.find('a',attrs={"itemprop":"url"})['href']
					uid = self.getID(uid)
					
					# get char name
					chname = a.find(attrs={"class":"character"}).text
					chname = self.shave(chname)
					indx = chname.find('/')
					chname = chname[:indx]
					# add it cast list
					if uid not in cast_list:
						cast_people[uid] = [chname,uid]
					
					# add it to person list
					if uid not in persons:
						persons[uid] = profile
					
					del profile
					del uid
					del chname
					del indx
			item['casts'] = cast_people
			del cast_list
			del cast_people
					
			# get story line
			sl = soup.find('div',attrs={"id":"titleStoryLine"})
			item['desc'] = self.shave(sl.find(attrs={"itemprop":"description"}).text)
			
			# now get genre
			g = sl.find(attrs={"itemprop":"genre"})
			genre = []
			for i in g.findAll('a'):
				genre.append(i.text)
			item['genre'] = genre
			del g
			del i
			del genre
			
			del sl
			
			# get details
			det = soup.find('div',attrs={"id":"titleDetails"})
			for row in det.findAll('div',attrs={"class":"txt-block"}):
				if row.h4 != None:
					txt = row.h4.text
					if txt == "Release Date:":
						item['realase_date'] = self.shave(row.contents[2])
					elif txt == "Budget:":
						item['budget'] = self.shave(row.contents[2])
					elif txt == "Gross:":
						item['gross'] = self.shave(row.contents[2])
					del txt
			del row
			del det
			
			
			# get facts
			dun = soup.find('div',attrs={"id":"titleDidYouKnow"})
			for row in dun.findAll('div',attrs={"class":"txt-block"}):
				if row.h4 != None:
					txt = row.h4.text
					if txt == "Trivia":
						item['trivia'] = self.shave(row.contents[2])
					elif txt == "Goofs":
						item['goofs'] = self.shave(row.contents[2])
					elif txt == "Quotes":
						item['quotes'] = self.shave(row.contents[2])
					del txt
			del row
			del dun
			
			
			
			return item,persons
		else:
			return None,None
		
		
	def createPerson(self,soup):
		url = soup['href']
		url = self.getID(url)
		name = soup.find(attrs={"itemprop":"name"}).text
		name = self.shave(name)
		return url,name
		
	def getID(self,url):
		url = url[1:]
		indx = url.find('/')
		indx = indx + 1
		url = url[indx:]
		indx = url.find('/')
		url = url[:indx]
		return url
		
	def shave(self,txt):
		txt = txt.replace('\n','')
		txt = txt.replace('\r','')
		txt = txt.strip()
		return txt


i = IMDBParser()
mov,human = i.parseMovie('tt2267998')
print mov
print human
