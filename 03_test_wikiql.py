import requests
from bs4 import BeautifulSoup
from neo4j import GraphDatabase
from wikipedia_ql import media_wiki

main_seasons = [
	"The Bachelor (American season 1)",
	"The Bachelor (American season 2)",
	# "The Bachelor (American season 3)", -- These don't have full pages?
	# "The Bachelor (American season 4)",
	"The Bachelor (American season 5)",
	# "The Bachelor (American season 6)",
	# "The Bachelor (American season 8)",
	"The Bachelor (American season 9)",
	"The Bachelor (American season 10)",
	"The Bachelor (American season 11)",
	"The Bachelor (American season 12)",
	"The Bachelor (American season 13)",
	"The Bachelor (American season 14)",
	"The Bachelor (American season 15)",
	"The Bachelor (American season 16)",
	"The Bachelor (American season 17)",
	"The Bachelor (American season 18)",
	"The Bachelor (American season 19)",
	"The Bachelor (American season 20)",
	"The Bachelor (American season 21)",
	"The Bachelor (American season 22)",
	"The Bachelor (American season 23)",
	"The Bachelor (American season 24)",
	"The Bachelor (American season 25)",
	"The Bachelor (American season 26)",
	"The Bachelorette (American season 1)",
	"The Bachelorette (American season 2)",
	"The Bachelorette (American season 3)",
	"The Bachelorette (American season 4)",
	"The Bachelorette (American season 5)",
	"The Bachelorette (American season 6)",
	"The Bachelorette (American season 7)",
	"The Bachelorette (American season 8)",
	"The Bachelorette (American season 9)",
	"The Bachelorette (American season 10)",
	"The Bachelorette (American season 11)",
	"The Bachelorette (American season 12)",
	"The Bachelorette (American season 13)",
	"The Bachelorette (American season 14)",
	"The Bachelorette (American season 15)",
	"The Bachelorette (American season 16)",
	"The Bachelorette (American season 17)",
	"The Bachelorette (American season 18)"]


para_seasons = [
	"Bachelor in Paradise (American season 1)",
	"Bachelor in Paradise (American season 2)",
	"Bachelor in Paradise (American season 3)",
	"Bachelor in Paradise (American season 4)",
	"Bachelor in Paradise (American season 5)",
	"Bachelor in Paradise (American season 6)",
	"Bachelor in Paradise (American season 7)",]

contestants_query = """ from "{}" {{
	    section[heading="Contestants"] >> table >> table-data >> tr {{
	    	td[column="Name"] as "name";
	    	td[column="Age"] as "age";
	    	td[column="Hometown"] as "hometown";
	    	td[column="Job"] as "job";
	    }}
	}}
"""

# WikiQL Parameterized Queries
MERGE_SHOW = """
	MERGE
		(s:Show {name: $name, season: $season})
	RETURN s"""

MERGE_PLAYER = """
	MERGE 
		(p:Player {name: $name}) 
	RETURN p"""
	
MERGE_R_STARRED = """
	MATCH 
		(p:Player {name: $p_name}), 
		(s:Show {name: $s_name, season: $season}) 
	MERGE (p)-[r:STARRED]->(s) 
	RETURN r;"""

MERGE_R_COMPETED = """
	MATCH 
		(p:Player {name: $p_name}), 
		(s:Show {name: $s_name, season: $season}) 
	MERGE (p)-[r:COMPETED]->(s) 
	RETURN r;"""


def processMainSeason(s_str, wiki):
	print("processing {}".format(s_str))
	s_tok = s_str.split(" ")
	show_name = "The {}".format(s_tok[1])
	show_season = int(s_tok[-1].replace(")",""))

	# Show/Season -> DB
	with driver.session() as session:
		session.run(MERGE_SHOW, name=show_name, season=show_season)

	# MVP -> DB
	s_url = "https://en.wikipedia.org/wiki/{}".format(s_str)
	response = requests.get(url=s_url)
	soup = BeautifulSoup(response.content, 'html.parser')

	infobox     = soup.find('table', {'class': 'infobox'})
	starring_td = infobox.find_all('th', text="Starring")
	mvp_name    = starring_td[0].parent.find('td').text
	print("MVP: {}".format(mvp_name))

	with driver.session() as session:
		session.run(MERGE_PLAYER, name=mvp_name)
		session.run(MERGE_R_STARRED, p_name=mvp_name, s_name=show_name, season=show_season)


	# Contestants -> Db
	with driver.session() as session:
		for row in wiki.query(contestants_query.format(s_str)):
			if len(row) > 0:
				print(row)
				session.run(MERGE_PLAYER, name=row['name'])
				session.run(MERGE_R_COMPETED, p_name=row['name'], s_name=show_name, season=show_season)


def processParaSeason(s_str, wiki):
	print("processing {}".format(s_str))
	s_tok = s_str.split(" ")
	show_name = "Paradise"
	show_season = int(s_tok[-1].replace(")",""))

	# Show/Season -> DB
	with driver.session() as session:
		session.run(MERGE_SHOW, name=show_name, season=show_season)

	with driver.session() as session:
		for row in wiki.query(contestants_query.format(s_str)):
			if len(row) > 0:
				print(row)
				session.run(MERGE_PLAYER, name=row['name'])
				session.run(MERGE_R_COMPETED, p_name=row['name'], s_name=show_name, season=show_season)


driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'));
wikipedia = media_wiki.Wikipedia()

for s in main_seasons:
	processMainSeason(s, wikipedia)

for ps in para_seasons:
	processParaSeason(ps, wikipedia)