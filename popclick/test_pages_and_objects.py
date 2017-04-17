""" 
* ©Copyrights, all rights reserved at the exception of the used libraries.
* @author: Phileas Hocquard 
* This file is used by tests.py
* Location : /mainsite/popclick/test_pages_and_objects.py
"""
import json

def page_one(auth):
	# Contains the representation of the main page at : https://immense-bastion-46341.herokuapp.com/
	return json.dumps({"profile":auth,"pageobjects":[["https://immense-bastion-46341.herokuapp.com/",
	"https://www.football.com/","FOOTBALL","html>body>div:eq(0)>div:eq(0)>a"],
	["https://immense-bastion-46341.herokuapp.com/","https://www.bloomberg.com/quote/DXY:CUR","DOLLARS",
	"html>body>div:eq(0)>div:eq(1)>a"],["https://immense-bastion-46341.herokuapp.com/","https://pencils.com/",
	"PENCILS","html>body>div:eq(0)>div:eq(2)>a"],["https://immense-bastion-46341.herokuapp.com/",
	"http://www.multiplication.com/","MULTIPLICATIONS","html>body>div:eq(1)>div:eq(0)>a"],
	["https://immense-bastion-46341.herokuapp.com/","https://harrypotter.com/","HARRY POTTER",
	"html>body>div:eq(1)>div:eq(1)>a"],["https://immense-bastion-46341.herokuapp.com/",
	"https://www.ft.com/?edition=uk","FINANCIAL TIMES","html>body>div:eq(1)>div:eq(2)>a"],
	["https://immense-bastion-46341.herokuapp.com/","","Close","html>body>div:eq(3)>div:eq(0)>a"]]})

def page_two(auth):
	# Contains the representation of the main page at : https://glacial-beyond-99420.herokuapp.com/ 
	return json.dump({"profile":auth,"pageobjects":[
		["https://glacial-beyond-99420.herokuapp.com/","http://www.freeminesweeper.org/",
		"MINESWEEPER","html>body>div:eq(0)>div:eq(0)>a"],
		["https://glacial-beyond-99420.herokuapp.com/","https://www.ferrari.com/",
		"FERRARI","html>body>div:eq(0)>div:eq(1)>a"],
		["https://glacial-beyond-99420.herokuapp.com/","http://www.lvbeethoven.com/Bio/BiographyLudwig.html",
		"BEETHOVEN","html>body>div:eq(0)>div:eq(2)>a"],
		["https://glacial-beyond-99420.herokuapp.com/","https://www.shoes.com/",
		"SHOES","html>body>div:eq(1)>div:eq(0)>a"],
		["https://glacial-beyond-99420.herokuapp.com/", "https://en.wikipedia.org/wiki/La_Fontaine%27s_Fables",
		"LA FONTAINE'S FABLES","html>body>div:eq(1)>div:eq(1)>a"],
		["https://glacial-beyond-99420.herokuapp.com/","https://immense-bastion-46341.herokuapp.com/","WEBSITE 1",
		"html>body>div:eq(1)>div:eq(2)>a"]]})

def page_two_objects(auth, item):
	# Returns the rightful page object for website 2
	object_list =[
		["https://glacial-beyond-99420.herokuapp.com/","http://www.freeminesweeper.org/",
		"MINESWEEPER","something","glacial-beyond-99420.herokuapp.com","/"],
		["https://glacial-beyond-99420.herokuapp.com/","https://www.ferrari.com/",
		"FERRARI","something","glacial-beyond-99420.herokuapp.com","/"],
		["https://glacial-beyond-99420.herokuapp.com/","http://www.lvbeethoven.com/Bio/BiographyLudwig.html",
		"BEETHOVEN","something","glacial-beyond-99420.herokuapp.com","/"],
		["https://glacial-beyond-99420.herokuapp.com/","https://www.shoes.com/",
		"SHOES","something","glacial-beyond-99420.herokuapp.com","/"],
		["https://glacial-beyond-99420.herokuapp.com/",	"https://en.wikipedia.org/wiki/La_Fontaine%27s_Fables",
		"LA FONTAINE'S FABLES","something","glacial-beyond-99420.herokuapp.com","/"],
		["https://glacial-beyond-99420.herokuapp.com/","https://immense-bastion-46341.herokuapp.com/",
		"WEBSITE 1","something","glacial-beyond-99420.herokuapp.com","/"]
		]
	return json.dumps({"profile":[auth,"2017-02-10 10:00"],"pageobject":object_list[item],"interaction":["ceate",1]})

def page_one_objects(auth, item):
		# Returns the rightful page object for website 1
	object_list =[
		["https://immense-bastion-46341.herokuapp.com/","https://www.football.com/","FOOTBALL",
		"html>body>div:eq(0)>div:eq(0)>a","https://immense-bastion-46341.herokuapp.com","/"],
		["https://immense-bastion-46341.herokuapp.com/","https://www.bloomberg.com/quote/DXY:CUR","DOLLARS",
		"html>body>div:eq(0)>div:eq(1)>a","https://immense-bastion-46341.herokuapp.com","/"],
		["https://immense-bastion-46341.herokuapp.com/","https://pencils.com/","PENCILS",
		"html>body>div:eq(0)>div:eq(2)>a","https://immense-bastion-46341.herokuapp.com","/"],
		["https://immense-bastion-46341.herokuapp.com/","http://www.multiplication.com/","MULTIPLICATIONS",
		"html>body>div:eq(1)>div:eq(0)>a","https://immense-bastion-46341.herokuapp.com","/"],
		["https://immense-bastion-46341.herokuapp.com/","https://harrypotter.com/","HARRY POTTER",
		"html>body>div:eq(1)>div:eq(1)>a","https://immense-bastion-46341.herokuapp.com","/"],
		["https://immense-bastion-46341.herokuapp.com/","https://www.ft.com/?edition=uk","FINANCIAL TIMES",
		"html>body>div:eq(1)>div:eq(2)>a","https://immense-bastion-46341.herokuapp.com","/"]
		]
	return json.dumps({"profile":[auth,"2017-02-10 10:00"],"pageobject":object_list[item],"interaction":["ceate",1]})


def made_up_profiles(item):
	object_list =[{"logtime":"2017-02-10 10:00","age":"18","gender":"Male",
			"interests":["Sports", "Travel", "Cars"], "signed":1},
			{"logtime":"2017-02-10 10:00","age":"18","gender":"Male",
			"interests":["Literature", "Movies & Theatre", "Craft"], "signed":1},
			{"logtime":"2017-02-10 10:00", "age":"18", "gender":"Female",
			"interests":["Literature", "Arts", "Craft"], "signed":1}]
	return json.dumps(object_list[item])