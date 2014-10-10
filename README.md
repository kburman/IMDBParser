IMDBParser
==========

It takes the ID of movie and then fetch the page and extract details from it and return you in structured way in which you can process.

#Requirments
- bs4 
- requests
```
	pip install bs4
	pip install requests
```
#How to 
```
i = IMDBParser()
movie,people = i.parseMovie('tt22679938')

print movie
print people
```
