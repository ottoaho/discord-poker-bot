import os
import random
from time import sleep
import discord

from discord.ext import commands
import poker_helpers

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
client = discord.Client()

async def get_message(message_id):
    await client.fetch_message(message_id)

def _format_poker_message(trx):
    money_emoji = '\U0001f4b8'
    pad_sum = f"{trx['sum']} €".rjust(5)
    return f"{trx['loser']}\t\t{money_emoji} {pad_sum}\t\t{trx['winner']}"


@bot.command(name='kalkuloi', help='Laskee pokeri-snipistä siirrot.')
async def poker_transactions(ctx):

    if isinstance(ctx, discord.Message):
        # automatic invocation by on_message
        poker_results_img = ctx.attachments[0]

    elif ctx.message.attachments:
        poker_results_img = ctx.message.attachments[0]

    else:
        raise ValueError("Where's the attachment?")

    print(f"Parsing {poker_results_img.url}")

    transactions = poker_helpers.calculate_poker_payouts(poker_results_img.url)
    for trx in transactions:
        print(trx)
        await ctx.channel.send(_format_poker_message(trx))


@bot.event
async def on_message(message):

    if message.author == client.user:
        return
    else:
        await bot.process_commands(message)

    if message.attachments:
        attachment = message.attachments[0]
        
        if attachment.width == 1440: # nokia 8 screen snip size
            await poker_transactions(message)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)