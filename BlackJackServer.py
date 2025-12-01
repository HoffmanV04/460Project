from socket import *
import random
from _thread import *

player_cards = []
dealer_cards = []
deck = []

def create_deck():
    ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    suits = ['H','D','C','S']
    deck = [r + s for r in ranks for s in suits]
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

def split():
  # only 2 cards and cards are equal
  if len(player_cards) == 2 and player_cards[0][0] == player_cards[1][0]:
    # create another hand and "hit" each hand with hit()
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
  
# TODO: needs to be implemented
def hit_player():
  # add card to hand
    global deck, player_cards, dealer_cards
    player_cards.append(deck.pop())
    return

def hit_dealer():
  # add card to hand
    global deck, player_cards, dealer_cards
    dealer_cards.append(deck.pop())
    return

def deal():
  # deal cards
  global deck, player_cards, dealer_cards
  deck = create_deck()
  player_cards.clear()
  dealer_cards.clear()
  for i in range(0,2):
    player_cards.append(deck.pop())
    dealer_cards.append(deck.pop())

  # check for dealer blackjack
  rank = dealer_cards[0][:-1] #gets the value of the card and not the suite
  if rank in{'J','Q','K','10'}:
    return "LOSE" if dealer_cards[1][:-1] == 'A' else ""
  elif rank == 'A':
    return "LOSE" if dealer_cards[1][:-1] in{'J','Q','K','10'} else ""
  return ""

# TODO: needs to be implemented
def finish_game():
  # deal to dealer until dealer has soft 17 or higher
    while hand_value(dealer_cards) < 17:
        hit_dealer
    
  return

def return_cards(cards):
  result = str(hand_value(cards)) + " "
  for card in cards:
    result = result + " " + card + " "
  return result

def blackjackThread(connectionSocket):
  print('Starting the thread for the blackjack game')
  clientRequest = connectionSocket.recv(1024).decode()
  print(clientRequest)
  requestCommand = clientRequest.split(' ')[0].strip()
  if requestCommand == 'LOGIN':
    # Prepare a welcome message with balance
    balance = 100 # change to allow storing balance. Store in file with username?
    welcomeMessage = 'LOGIN ' + str(balance)
    connectionSocket.send(welcomeMessage.encode())

    player_bet = connectionSocket.recv(1024).decode().split(' ')[1]
    # TODO: implement input validation. send 'invalid' on error
    print(f"Bet: {player_bet}")
    connectionSocket.send(player_bet.encode())
    # deal cards to dealer and player
    if deal() == "LOSE":
      connectionSocket.send("RESULT dealer_blackjack".encode())
      connectionSocket.close()
      return
    while True:
      gameCommand = connectionSocket.recv(1024).decode().split(' ')
      print(f"GAME COMMAND: {gameCommand}")
      action = gameCommand[0]
      if action == "HIT":
        hit_player()
      elif action == "STAND":
        finish_game()
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
          result = "error bad command"
      
      connectionSocket.send(result.encode())
        
      
      if "error" in result:
        # error doubling or splitting cards
        # send appropriate message
        connectionSocket.close()
        return
      
      player_total = hand_value(player_cards)
      if player_total > 21:
        result = "RESULT player_bust"
        break
      elif player_total == 21:
        result = "RESULT player_blackjack"
        break
      dealer_total = hand_value(player_cards)
      if hand_value(dealer_cards) > 21:
        result = "RESULT dealer_bust"
        break
      elif hand_value(dealer_cards) == 21:
        result = "RESULT dealer_blackjack"
        break
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
    print(f"RESULT: {result}")
    connectionSocket.send(result.encode())
  connectionSocket.close()

def serverMain():
  serverPort = 12346
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











