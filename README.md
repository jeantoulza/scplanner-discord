
SCPlanner Discord bot
===================

SCPlanner Discord bot is a Discord bot designed to make reposts easier and faster by using Discord.

Commands
-------
`!repost <track-link>` : autoschedule a track and replies with the calendar link.

Installation
-------
1. Clone this repo.
2. Configure `config.ini` to your needs.
3. Run `pip install -r requirements.txt`
4. Run `python bot.py`

Configuration
-------

 - `cookie_name` : This is the session cookie name. Do not change it to anything else than `ci_session` at the moment.
 - `cookie_value` : Your session cookie value. Log in on SCPlanner with your repost account and open up your browser developer view, then grab the `ci_session` cookie value.
 - `bot_token` : Get yours on [Discord developers portal](https://discordapp.com/developers/applications/me).
 - `reposters_role` : Only members of this role on your server will be able to use the `!repost` command.
 - `use_all_accounts` : If set to `no` (default), the bot will use account preferences to schedule your repost. If set to `yes`, the bot will use **all** subs to schedule the repost.
 
Invite on your server
-------

1. Go to your app details on [Discord developers portal](https://discordapp.com/developers/applications/me).
2. Hit the `Generate OAuth2 URL` button.
	![Generate OAuth2 URL](https://cdn.discordapp.com/attachments/335156054297935874/434004913434001419/unknown.png)
3. Copy the link with the default settings.
	![Copy](https://cdn.discordapp.com/attachments/335156054297935874/434005008778919939/unknown.png)
4. Paste it in your browser, then proceed to add the bot on your server.