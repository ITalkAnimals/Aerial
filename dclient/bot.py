#!/usr/bin/python3
import discord
import asyncio
import ssl
import websockets
import json
import requests
import logging as log
import handle
import socket
from random import shuffle
from sys import exc_info as exc
from yaml import safe_load
from mysql.connector import connect as dbconnect
from discord.ext import commands
from discord.ext import tasks

config = safe_load(open("config.yml", "r"))
cert = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT).load_verify_locations("ssl/cert.pem")
active = {}
using = {}
client = commands.AutoShardedBot(
    command_prefix=["a.", "A."],
    case_insensitive=True,
    help_command=None,
)
can_start = True
db = dbconnect(
    host=config["Database"]["Host"],
    port=config["Database"]["Port"],
    user=config["Database"]["Username"],
    password=config["Database"]["Password"],
    database="aerial",
)
db.autocommit = True
log.basicConfig(
    filename="dclient.log",
    format="DClient @ %(asctime)s | %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=log.INFO,
)

# Check WebSocket Connection
async def wswait(accmsg: discord.Message):
    await asyncio.sleep(10)
    if type(accmsg.edited_at) is None:
        await accmsg.edit(
            embed=discord.Embed(
                title="<:Offline:719321200098017330> Bot Offline",
                description="Cannot establish a WebSocket connection.\nThis is likely because the server is offline.",
                color=0x747F8D,
            )
        )
        await active[accmsg.author.id].close(code=1000, reason="Timeout")
        active.pop(accmsg.channel.recipient.id, None)
        using.pop(accmsg.channel.recipient.id, None)


# Boost Check
async def is_boosting(id: int):
    g = client.get_guild(71884230999880502)
    member = g.get_member(id)
    if member is None:
        return False
    elif member in g.premium_subscribers:
        return True
    else:
        return False


# Main WebSocket Handler
async def wsconnect(user):

    try:
        accmsg = await user.send(
            embed=discord.Embed(
                title="<a:Loading:719025775042494505> Starting Bot...",
                description="Looking for an available node...",
                color=0x7289DA,
            )
        )
    except discord.Forbidden:
        return

    if not can_start:
        await accmsg.edit(
            embed=discord.Embed(
                title=":x: Bot Creation is Disabled",
                description="Bot creation has been temporarily disabled.\nThis is most likely due to an update.",
                color=0xE46B6B,
            ),
            delete_after=10,
        )
        return

    shuffle(config["Nodes"])
    for node in config["Nodes"]:
        await accmsg.edit(
            embed=discord.Embed(
                title="<a:Loading:719025775042494505> Starting Bot...",
                description=f"Attempting to connect to `{node}`...",
                color=0x7289DA,
            )
        )

        # Check to see if port is open, i.e. server is up
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        await asyncio.sleep(2)
        if s.connect_ex((node, 8765)) != 0:
            s.close()
            continue
        s.close()

        # Connect to the server
        async with websockets.connect(
            f"wss://{node}:8765", ssl=cert, ping_interval=10, ping_timeout=10
        ) as ws:

            try:
                async for message in ws:
                    cmd = json.loads(message)
    
                    if cmd["type"] == "no_free_accounts":
                        continue
    
                    elif cmd["type"] == "account_info":
                        active[user.id] = [ws]
                        img = requests.get(
                            "https://benbotfn.tk/api/v1/cosmetics/br/" + cmd["outfit"]
                        ).json().get("icons", {}).get("icon", "")
                        await accmsg.edit(
                            embed=discord.Embed(
                                title="<:Online:719038976677380138> " + cmd["username"],
                                color=0xFC5FE2,
                            )
                            .set_thumbnail(url=img)
                            .add_field(
                                name="Discord Server",
                                value="https://discord.gg/fn8UfRY",
                            )
                            .add_field(
                                name="Documentation", value="https://aerial.now.sh/"
                            )
                        )
    
                    elif cmd["type"] == "shutdown":
                        await accmsg.edit(
                            embed=discord.Embed(
                                title="<:Offline:719321200098017330> Bot Offline",
                                description=cmd["content"],
                                color=0x747F8D,
                            )
                        )
                        active.get(user.id, []).remove(ws)
                        if active.get(user.id, []) == []:
                            active.pop(user.id, None)
                        return
    
                    elif cmd["type"] == "fail" or cmd["type"] == "success":
                        await handle.feedback(cmd, user)
    
                    elif cmd["type"] == "incoming_fr" or cmd["type"] == "incoming_pi":
                        await handle.incoming(cmd, user, client, ws)
    
                    else:
                        await user.send("```json\n" + json.dumps(cmd) + "```")

            except websockets.exceptions.ConnectionClosedError:
                if active.get(user.id, None) is None:
                    continue
                else:
                    await accmsg.edit(
                        embed=discord.Embed(
                            title="<:Offline:719321200098017330> Bot Offline",
                            description="The WebSocket connection was lost.",
                            color=0x747F8D,
                        )
                    )
                    active.get(user.id, []).remove(ws)
                    if active.get(user.id, []) == []:
                        active.pop(user.id, None)
                    return

            except websockets.exceptions.ConnectionClosedOK:
                if active.get(user.id, None) is None:
                    continue
                else:
                    await accmsg.edit(
                        embed=discord.Embed(
                            title="<:Offline:719321200098017330> Bot Offline",
                            description="The WebSocket connection was lost.",
                            color=0x747F8D,
                        )
                    )
                    active.get(user.id, []).remove(ws)
                    if active.get(user.id, []) == []:
                        active.pop(user.id, None)
                    return

            except:
                pass

    await accmsg.edit(
        embed=discord.Embed(
            title=":x: No Free Accounts",
            description="There are currently no free accounts available.\nPlease try again later.",
            color=0xE46B6B,
        ),
        delete_after=10,
    )


@client.event
async def on_message(message: discord.Message):
    if (type(message.channel) == discord.DMChannel) and (
        message.author.id in list(active.keys())
    ):
        for ws in active[message.author.id]:
            try:
                await handle.command(message, ws)
            except:
                pass
    elif message.channel.id == 718979003968520283 and "start" in message.content.lower():
        if message.author.id in list(active.keys()):
            await message.author.send(
                embed=discord.Embed(title=":x: Bot Already Running!", color=0xE46B6B),
                delete_after=10,
            )
        else:
            await wsconnect(message.author)
    else:
        await client.process_commands(message)


@client.command(aliases=["startbot", "create"])
async def start(ctx):
    if ctx.message.author.id in list(active.keys()):
        await ctx.message.author.send(
            embed=discord.Embed(title=":x: Bot Already Running!", color=0xE46B6B),
            delete_after=10,
        )
    # elif len(active.get(ctx.message.author.id, [])) >= 3:
    #    await ctx.message.author.send(
    #        embed=discord.Embed(title=":x: Account Limit Reached!", color=0xE46B6B),
    #        delete_after=10,
    #    )
    else:
        await wsconnect(ctx.message.author)


@client.command(aliases=["stop"])
async def kill(ctx, user: discord.User = None):
    if ctx.message.author.id == 406856161015627835 and user is not None:
        for ws in list(active.get(ctx.message.author.id, [])):
            active[user.id].remove(ws)
            try:
                await ws.send(json.dumps({"type": "stop"}))
            except:
                pass
        await ctx.send(f"<:Accept:719047548219949136> {user.mention} Stopped Session!")
        if active[user.id] == []:
            active.pop(user.id, None)
    elif ctx.message.author.id in list(active.keys()):
        for ws in list(active.get(ctx.message.author.id, [])):
            active[ctx.message.author.id].remove(ws)
            try:
                await ws.send(json.dumps({"type": "stop"}))
            except:
                pass
        await ctx.send(
            f"<:Accept:719047548219949136> {ctx.message.author.mention} Stopped Session!"
        )
        if active[ctx.message.author.id] == []:
            active.pop(ctx.message.author.id, None)
    else:
        await ctx.send(
            f"<:Reject:719047548819472446> {ctx.message.author.mention} You do not have an active bot! Type `a.start` to create one!"
        )


@client.command(hidden=True)
async def disable(ctx):
    global can_start
    if ctx.message.author.id == 406856161015627835:
        can_start = False


@client.command(hidden=True)
async def enable(ctx):
    global can_start
    if ctx.message.author.id == 406856161015627835:
        can_start = True


@client.command(hidden=True)
async def killall(ctx):
    if ctx.message.author.id == 406856161015627835:
        for u in list(active.keys()):
            await u.send(":stop_sign: This bot has been stopped.")
            for ws in active[u]:
                await ws.close()


@client.command(hidden=True)
async def sendall(ctx, *, message: str):
    if ctx.message.author.id == 406856161015627835:
        for u in list(active.keys()):
            await u.send(message)


@client.command()
async def help(ctx):
    commands = {
        "start": "Starts the bot for 3 hours.",
        "kill": "Stops the bot outside of DMs.",
        "help": "Shows this message.",
    }
    cmdlist = ""
    for c in commands:
        cmdlist = f"{cmdlist}`{c}` - {commands[c]}\n"
    await ctx.send(
        embed=discord.Embed(
            title="Aerial Commands", description=cmdlist, color=0xFC5FE2
        ).set_footer(text="Support Server: https://discord.gg/fn8UfRY")
    )


@tasks.loop(minutes=5.0)
async def counter():
    c1 = await client.fetch_channel(727599283179749466)
    c2 = await client.fetch_channel(720787276329910363)
    c = db.cursor()
    c.execute("""SELECT COUNT(*) FROM `accounts` WHERE `in_use` = '1';""")
    running = c.fetchone()[0]
    c.execute("""SELECT COUNT(*) FROM `accounts`;""")
    all = c.fetchone()[0]
    name1 = f"{len(client.guilds)} Servers"
    name2 = f"{running}/{all} Clients Running"
    await c1.edit(name=name1)
    await c2.edit(name=name2)


@counter.before_loop
async def before_counter():
    await client.wait_until_ready()


@client.event
async def on_ready():
    counter.start()


@client.event
async def on_shard_ready(shard_id: int):
    await client.change_presence(
        activity=discord.Streaming(
            platform="Twitch",
            name=f"Fortnite Bots | SH{shard_id}",
            url="https://twitch.tv/andre4ik3",
        ),
        shard_id=shard_id,
    )


if __name__ == "__main__":
    client.run(config["Token"])
    for u in list(active.keys()):
        for ws in active[u]:
            asyncio.get_event_loop().create_task(ws.close())
