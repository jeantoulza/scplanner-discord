SCPlanner Discord bot
===================

SCPlanner Discord bot is a Discord bot designed to make reposts easier and faster by using Discord.

Commands
-------
`!repost <track-link>` : autoschedule a track **with all accounts** and replies with the calendar link.

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