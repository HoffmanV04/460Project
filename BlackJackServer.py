from socket import *
import random

HOST = 
PORT = 

user_balances = {}
INITIAL_BALANCE = 1000

def create_deck():
    ranks ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    suits = ['H','D','C','S']
    deck = [r + s for r in ranks s in suits]
    random.shuffle(deck)
    return deck

def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        rank = card[:-1] #gets the value of the card and not the suite
        if rank in{'J','Q','K'}:
            total += 10
        elif rank == 'A':
            total += 11
            aces += 1
        else:
            total += int(rank)
    #adjust aces from 11 to 1 if needed
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total
