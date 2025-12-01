from socket import *
import random
from _thread import *
import time

player_cards = []
dealer_cards = []
deck = []
bet = 0


def create_deck():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['H', 'D', 'C', 'S']
    deck = [r + s for r in ranks for s in suits]
    random.shuffle(deck)
    return deck


def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        rank = card[:-1]  # gets the value of the card and not the suite
        if rank in {'J', 'Q', 'K'}:
            total += 10
        elif rank == 'A':
            total += 11
            aces += 1
        else:
            total += int(rank)
    # adjust aces from 11 to 1 if needed
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def split():
    # only 2 cards and cards are equal
    if len(player_cards) == 2 and player_cards[0][0] == player_cards[1][0]:
        bet = bet * 2
        return "ACTION"
    else:
        return "error invalid cards"


def double():
    if len(player_cards) == 2:
        hit_player()
        bet = bet * 2
        return "RESULT"
    else:
        return "error invalid cards"


def hit_player():
    # add card to hand
    global deck, player_cards
    player_cards.append(deck.pop())
    player_total = hand_value(player_cards)
    if player_total > 21:
        return "RESULT player_bust"
    elif player_total == 21:
        return "RESULT player_win"
    return "ACTION"


def hit_dealer():
    # add card to hand
    global deck, dealer_cards
    dealer_cards.append(deck.pop())
    dealer_total = hand_value(dealer_cards)
    if dealer_total > 21:
        return "RESULT dealer_bust"
    elif dealer_total == 21:
        return "RESULT dealer_win"
    return "ACTION"


def deal():
    # deal cards
    global deck, player_cards, dealer_cards
    deck = create_deck()
    player_cards.clear()
    dealer_cards.clear()
    for i in range(0, 2):
        player_cards.append(deck.pop())
        dealer_cards.append(deck.pop())



        # check for player blackjack
    player_rank = player_cards[0][:-1]  # gets the value of the card and not the suite
    if player_rank in {'J', 'Q', 'K', '10'}:
        return "WIN" if player_cards[1][:-1] == 'A' else ""
    elif player_rank == 'A':
        return "WIN" if player_cards[1][:-1] in {'J', 'Q', 'K', '10'} else ""
    # check for dealer blackjack
    rank = dealer_cards[0][:-1]  # gets the value of the card and not the suite
    if rank in {'J', 'Q', 'K', '10'}:
        return "LOSE" if dealer_cards[1][:-1] == 'A' else ""
    elif rank == 'A':
        return "LOSE" if dealer_cards[1][:-1] in {'J', 'Q', 'K', '10'} else ""
    return ""


def finish_game():
    global dealer_cards
    result = ""
    # deal to dealer until dealer has soft 17 or higher
    while hand_value(dealer_cards) < 17:
        result = hit_dealer()
    return result


def return_cards(cards):
    result = str(hand_value(cards)) + " "
    for card in cards:
        result = result + " " + card + " "
    return result


def blackjackThread(connectionSocket):
    print('Starting the thread for the blackjack game')
    clientRequest = connectionSocket.recv(1024).decode()
    requestCommand = clientRequest.split(' ')[0].strip()
    while True:
        if requestCommand == 'LOGIN':
            # Prepare a welcome message with balance
            balance = 100  # change to allow storing balance. Store in file with username?
            welcomeMessage = 'LOGIN ' + str(balance)
            connectionSocket.send(welcomeMessage.encode())

            player_bet = connectionSocket.recv(1024).decode().split(' ')[1]
            if player_bet.isdigit() and (int(player_bet) < 0 or int(player_bet) > 100):
                connectionSocket.send("invalid".encode())
            # deal the cards and return result if the player or dealer gets blackjack
            result = deal()
            if result == "LOSE":
                connectionSocket.send("RESULT dealer_blackjack".encode())
                connectionSocket.close()
                break
            elif result == "WIN":
                connectionSocket.send("RESULT player_blackjack".encode())
                connectionSocket.close()
                break
            # echo the player's bet
            connectionSocket.send(player_bet.encode())
            # deal cards to dealer and player
            while True:
                gameCommand = connectionSocket.recv(1024).decode().split(' ')
                action = gameCommand[0]
                if action == "HIT":
                    result = hit_player()
                elif action == "STAND":
                    result = finish_game()
                    break
                elif action == "DOUBLE":
                    result = double()
                elif action == "SPLIT":
                    result = split()
                elif action == "GET":
                    if gameCommand[1] == "dealer":
                        result = "HAND " + return_cards(dealer_cards)
                    elif gameCommand[1] == "player":
                        result = "HAND " + return_cards(player_cards)
                    else:
                        break

                if "RESULT" in result:
                    break
                connectionSocket.send(result.encode())

            # end while
            if "RESULT" in result:
                connectionSocket.send(result.encode())
            else:
                player_total = hand_value(player_cards)
                dealer_total = hand_value(dealer_cards)
                if player_total < dealer_total:
                    # player loses
                    result = "RESULT dealer_win"
                elif player_total == dealer_total:
                    # push
                    result = "RESULT push"
                else:
                    # player win
                    result = "RESULT player_win"
                connectionSocket.send(result.encode())
    time.sleep(1)
    connectionSocket.close()


def serverMain():
    serverPort = 12348
    # Create a welcome TCP scocket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)
    print('The blackjack game server is ready!')

    while True:
        # Create connection socket when sensing new connection request
        connectionSocket, addr = serverSocket.accept()
        start_new_thread(blackjackThread, (connectionSocket,))


serverMain()

