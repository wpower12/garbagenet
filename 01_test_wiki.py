import pywikibot

msf_page = "List_of_The_Bachelor_(American_TV_series)_episodes#Series_overview"
fsm_page = "List_of_The_Bachelorette_(American_TV_series)_episodes#Series_overview"

site = pywikibot.Site()

msf = pywikibot.Page(site, msf_page)
fsm = pywikibot.Page(site, fsm_page)

seasons = set()

def add_seasons(s, src_page):
	for t in src_page.templates():
		if ("American season" in t.title()) and t.namespace() == 0:
			for t_s0 in t.templates():
				if "American season" in t_s0.title() and t_s0.namespace() == 0:
					if t_s0 not in s:
						s.add(t_s0.title())

add_seasons(seasons, msf)
add_seasons(seasons, fsm)

s_seasons = sorted(list(seasons))

for s in s_seasons:
	print(s)
