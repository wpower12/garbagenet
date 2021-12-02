import requests
from bs4 import BeautifulSoup
from neo4j import GraphDatabase

# NOTE - this does not work. season wiki html is not as uniform as i'd hoped. 

MERGE_PLAYER = """
	MERGE 
		(p:Player {name: $name}) 
	RETURN p"""

MERGE_SHOW = """
	MERGE
		(s:Show {name: $name, season: $season})
	RETURN s"""
	
MERGE_R_COMPETED = """
	MATCH 
		(p:Player {name: $p_name}), 
		(s:Show {name: $s_name, season: $season}) 
	MERGE (p)-[r:COMPETED]->(s) 
	RETURN r;"""

seasons = [
	"https://en.wikipedia.org/wiki/The Bachelor (American season 1)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 2)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 3)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 4)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 5)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 6)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 8)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 9)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 10)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 11)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 12)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 13)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 14)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 15)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 16)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 17)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 18)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 19)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 20)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 21)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 22)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 23)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 24)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 25)",
	"https://en.wikipedia.org/wiki/The Bachelor (American season 26)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 1)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 2)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 3)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 4)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 5)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 6)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 7)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 8)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 9)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 10)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 11)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 12)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 13)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 14)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 15)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 16)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 17)",
	"https://en.wikipedia.org/wiki/The Bachelorette (American season 18)"]


def processSeason(s_url, driver):

	ss_tokens = s_url.split("/")[4].split(" ")
	show_name = ss_tokens[0]+" "+ss_tokens[1]
	show_season = int(ss_tokens[-1].replace(")", ""))

	print(show_name, show_season)
	with driver.session() as session:
		session.run(MERGE_SHOW, name=show_name, season=show_season)

	response = requests.get(url=s_url)
	soup = BeautifulSoup(response.content, 'html.parser')

	vip_table = soup.find_all("table")[0]
	vip_name  = vip_table.find_all("tr")[3].find("a").text
	print("!!! "+vip_name)

	with driver.session() as session:
		for contestant_row in soup.find_all("table")[1].find_all("tr"):
			if len(contestant_row.find_all("td")) > 0:
				td = contestant_row.find_all("td")[0]
				contestant_name = td.text.strip('\n')
				print(contestant_name)
				session.run(MERGE_PLAYER, name=contestant_name)
				session.run(MERGE_R_COMPETED, p_name=contestant_name, s_name=show_name, season=show_season)


driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'));
for s in seasons:
	processSeason(s, driver)

driver.close()