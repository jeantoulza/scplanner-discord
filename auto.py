import mechanicalsoup
import json
import requests
import soundcloud
import re
import discord
from discord.ext import commands
import asyncio
from bs4 import BeautifulSoup
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

BASE = "https://scplanner.net/"
COOKIE_NAME = config["CONFIG"]["cookie_name"]
COOKIE_VALUE = config["CONFIG"]["cookie_value"]

print(COOKIE_NAME+"="+COOKIE_VALUE)

def get_cookie_jar():
		try:
			from cookielib import Cookie, CookieJar         # Python 2
		except ImportError:
			from http.cookiejar import Cookie, CookieJar    # Python 3.
			from http.cookies import SimpleCookie
		cj = CookieJar()
		# Cookie(version, name, value, port, port_specified, domain, 
		# domain_specified, domain_initial_dot, path, path_specified, 
		# secure, discard, comment, comment_url, rest)
		c = Cookie(version=0, name=COOKIE_NAME, value=COOKIE_VALUE, port=None, port_specified=False, domain='scplanner.net', 
			   domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest=None, rfc2109=True)
		cj.set_cookie(c)
		return cj
		
def resolve(url):
	client_id = "nF5U0gNsNB8529U1rHetpIywdIlnEKk7"
	client = soundcloud.Client(client_id=client_id)
	try:
		track = client.get("/resolve?url="+url)
		return track
	except:
		new_client_id = get_client_id()
		if not new_client_id:
			return False
		try:
			client = soundcloud.Client(client_id=new_client_id)
			track = client.get("/resolve?url="+url)
			return track
		except:
			return False
			
def get_client_id():
	body = requests.get("https://soundcloud.com").text
	reg_app = r'https:\/\/a-v2\.sndcdn\.com\/assets\/app(.*).js'
	matches = re.search(reg_app,body)
	if matches:
		app_url = matches.group()
		app_content = requests.get(app_url).text
		reg_cid = r'client_id:"(\w+)"'
		matches = re.search(reg_cid, app_content)
		if matches:
			client_id = matches.group(1)
			return client_id
		else:
			return False
	else:
		return False

def auto(track_url):
	"""Autoschedule a track link."""
	br = mechanicalsoup.StatefulBrowser()
	cj = get_cookie_jar()
	br.set_cookiejar(cj)
			
	rep = br.open(BASE+"network")
	soup = BeautifulSoup(rep.text, "html.parser")
	try:
		user_url = soup.find("input", {"class": "form-control"})["value"]
		soundcloud_id = resolve(user_url).id
	except:
		raise Exception("Could not determine logged in user...")
	
	rep = br.open(BASE+"schedule")
		
	try:
		br.select_form("#autoschForm")
		br["urls"] = track_url
		soup = BeautifulSoup(rep.text, "html.parser")
		accounts_select = soup.find("select", {"name": "account[]"})
		accounts = []
		for account_option in accounts_select.findAll("option"):
			accounts.append(account_option["value"])
		br["account[]"] = tuple(accounts)
		#br["account[]"] = (107375074, 195766419)
		rep = br.submit_selected()
	except:
		raise Exception("ERROR 131: There was a problem when posting URL on SCPlanner. Is your account still valid?")
	
	rep = rep.text
	
	rep_json = json.loads(rep)
	if not isinstance(rep_json, list):
		if rep_json["title"] == "Error S-788":
			raise Exception("You have not set your account preferences. Please set them here: https://scplanner.net/account")
		else:
			print(rep_json)
			raise Exception("Something weird happened. Please tell Amazed#3330.")
	type = rep_json[0]["type"]
	if type == "success" and len(rep_json[0]["success_schedules"]) > 0:
		group = rep_json[0]["success_schedules"][0]["group"]
		text = rep_json[0]["text"]
		track = resolve(track_url)
		if track:
			return text+"\nSee https://scplanner.net/calendar/reposts/{0}/{1}/{2}".format(soundcloud_id, track.id, group)
		else:
			raise Exception("ERROR 312: Schedule was done but I could not find track :( Please PM Amazed#3330.")
	else:
		raise Exception("ERROR 851: Track not found :(")

		
def start_bot():
	bot = commands.Bot(command_prefix='!')
	@bot.event
	async def on_ready():
		print('Logged in as')
		print(bot.user.name)
		print(bot.user.id)
		print('------')
		
	@bot.command()
	async def repost(url : str):
		"""Reposts an URL on SCPlanner."""
		try:
			calendar_link = auto(url)
			await bot.say(calendar_link)
		except Exception as e:
			await bot.say("ERROR: "+str(e))

	bot.run(config["CONFIG"]["bot_token"])
	
if __name__ == '__main__':
	start_bot()
	#auto("https://soundcloud.com/toto/totooooo")