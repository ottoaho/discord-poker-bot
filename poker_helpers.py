from pytesseract import image_to_string
from PIL import Image 
import requests
from io import BytesIO
import re

def _get_image_text(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return image_to_string(img, config='--psm 12')

def get_payouts_from_image(image_url):
    text = _get_image_text(image_url)
    payout_matches = re.findall('(\n([\w ]+)\n{2}([+-]\d+)\n)+?', text)
    return { m[1]: int(m[2]) for m in payout_matches }

def calculate_poker_payouts(poker_screenshot_url):

    def allocate_losses(winner, loser):
        """Take one unit from loser's payables and allocate it to winner"""
        trx_sum = 0
        while payables[loser] > 0 and payables[winner] < 0:
            payables[loser] -= 1
            payables[winner] += 1
            trx_sum +=1

        return trx_sum

    payouts = get_payouts_from_image(poker_screenshot_url)
    payables = { plr: -sum for plr, sum in payouts.copy().items() }

    winners = [ plr for plr, net in payouts.items() if net > 0]
    losers = [ plr for plr, net in payouts.items() if net < 0]

    transactions = []
    
    for winner in winners:
        for loser in losers:

            if payables[winner] == 0 or payables[loser] == 0:
                continue

            trx = {
                    "loser": loser,
                    "winner": winner,
                    "sum": 0 
                }
            trx["sum"] = allocate_losses(winner, loser)

            transactions.append(trx)

    for player, winnings in payouts.items():
        trx_net_sum = -sum([trx["sum"] for trx in transactions if trx["loser"] == player])
        trx_net_sum += sum([trx["sum"] for trx in transactions if trx["winner"] == player])
        try: 
            assert trx_net_sum == winnings, "Something doesn't add up..."
        except AssertionError as err:
            print(err)

    return transactions

