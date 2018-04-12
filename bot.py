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

def get_cookie_jar():
	'''
	Creates a cookie jar for the mechanicalsoup browser
	'''
	from http.cookiejar import Cookie, CookieJar
	cj = CookieJar()
	c = Cookie(version=0, name=COOKIE_NAME, value=COOKIE_VALUE, port=None, port_specified=False, domain='scplanner.net', 
		   domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest=None, rfc2109=True)
	cj.set_cookie(c)
	return cj
		
def resolve(url):
	'''
	Transforms a 'url' into a soundcloud object. False if not found.
	'''
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
	'''
	Tricky part to get the current public client_id of SoundCloud's website
	'''
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
		
		use_all_accounts = False
		try:
			if config["AUTO"]["use_all_accounts"] == "yes":
				soup = BeautifulSoup(rep.text, "html.parser")
				accounts_select = soup.find("select", {"name": "account[]"})
				accounts = []
				for account_option in accounts_select.findAll("option"):
					accounts.append(account_option["value"])
				br["account[]"] = tuple(accounts)
				#br["account[]"] = (107375074, 195766419)
		except:
			pass
		rep = br.submit_selected()
	except:
		raise Exception("There was a problem when posting URL on SCPlanner. Is your account still valid?")
	
	rep = rep.text
	
	rep_json = json.loads(rep)
	if not isinstance(rep_json, list):
		if rep_json["title"] == "Error S-788":
			raise Exception("You have probably set use_all_accounts to 'no' and have not set your account preferences. Please set them here: https://scplanner.net/account")
		else:
			print(rep_json)
			raise Exception("Unknown error. Please fill an issue on https://github.com/jeantoulza/scplanner-discord.")
	type = rep_json[0]["type"]
	if type == "success" and len(rep_json[0]["success_schedules"]) > 0:
		group = rep_json[0]["success_schedules"][0]["group"]
		text = rep_json[0]["text"]
		track = resolve(track_url)
		if track:
			return text+"\nSee https://scplanner.net/calendar/reposts/{0}/{1}/{2}".format(soundcloud_id, track.id, group)
		else:
			raise Exception("Schedule was done but I could not find track :(")
	else:
		raise Exception("Track not found, or something worse happened :(")

def has_role(user, role):
	'''
	Returns True if 'user' has the 'role' role, False otherwise.
	'''
	for u_role in user.roles:
		if u_role.name == role:
			return True
	return False
		
def start_bot():
	'''
	Main bot loop
	'''
	bot = commands.Bot(command_prefix='!')
	@bot.event
	async def on_ready():
		print('Logged in as')
		print(bot.user.name)
		print(bot.user.id)
		print('------')
		
	@bot.command(pass_context=True)
	async def repost(ctx, url : str):
		"""Reposts an URL on SCPlanner."""
		user = ctx.message.author
		if not isinstance(user, discord.Member):
			await bot.say("Please use this command in a server that the bot is located in.")
			return
			
		if not has_role(user, config["CONFIG"]["reposters_role"]):
			await bot.say("You do not have the required role to repost or use this bot.")
			return
		try:
			calendar_link = auto(url)
			await bot.say(calendar_link)
		except Exception as e:
			await bot.say("ERROR: "+str(e))

	bot.run(config["CONFIG"]["bot_token"])
	
if __name__ == '__main__':
	start_bot()
	#auto("https://soundcloud.com/toto/totooooo")
