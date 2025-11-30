from socket import *

def displayResult(result):
    game_result=result[1]
    wins = ["player_blackjack", "player_win", "dealer_bust"]
    loses = ["dealer_win", "player_bust", "dealer_blackjack"]

    if game_result.lower() in wins:
        print("You Win!" + game_result)
    elif game_result.lower() in loses:
        print("Dealer Wins! " + game_result)
    elif game_result.lower() == "push":
        print("Push, no winner")
    return


def displayDealer(clientSocket):
    dealerRequest = "GET dealer"
    clientSocket.send(dealerRequest.encode())
    #expects response in form DEALER <value> <card1> <card2> ...
    dealerResponse = clientSocket.recv(1024).decode()
    dealer_hand=dealerResponse.split()
    message = dealer_hand.pop(0)
    # initialize the dealer's hand, and the value of what it's showing
    dealer_value = dealer_hand.pop(0)

    display_hand = "Dealer Hand: "
    #Dealer's cards:
    for card in dealer_hand:
        display_hand += card + " "
    #print the dealer's hand
    print("--------------------------------")
    print(display_hand)
    #Total the dealer is showing
    print("Dealer Total: " + dealer_value)
    print("--------------------------------" + "\n")


def displayPlayer(clientSocket):
    playerRequest = "GET player"
    clientSocket.send(playerRequest.encode())
    #expects response in form "PLAYER <value> <card1> <card2> ..."

    playerResponse = clientSocket.recv(1024).decode()
    player_hand=playerResponse.split()
    player_hand.pop(0)
    # initialize player's hand and the value of it
    player_value = player_hand.pop(0)

    display_hand = "Your Hand: "
    #Player's  card:
    for card in player_hand:
        display_hand += card + " "
    #print the player's hand
    print("--------------------------------")
    print(display_hand)
    #Total of the hand
    print("Your Total: " + player_value + "\n")
    print("--------------------------------" + "\n")




    return

def sendAction(clientSocket, action):
    action = action.encode()
    clientSocket.send(action)

def playHand(clientSocket):
    while True:
        print("\nChoose an action:")
        print("(1) Hit")
        print("(2) Stand")
        print("(3) Double (first turn only)")
        print("(4) Split (only if allowed)")

        choice = input("Enter choice: ")

        if choice == '1':
            sendAction(clientSocket, "HIT")
        elif choice == '2':
            sendAction(clientSocket, "STAND")
        elif choice == '3':
            sendAction(clientSocket, "DOUBLE")
        elif choice == '4':
            sendAction(clientSocket, "SPLIT")
        else:
            print("Invalid input.")
            continue

        actionResponse = clientSocket.recv(1024).decode()
        response = actionResponse.split()

        #view updated hands
        displayDealer(clientSocket)
        displayPlayer(clientSocket)

        #the next step
        if "RESULT" in response: #when the game ends and returns the result
            displayResult(response)
            return

        if "NEXT_HAND" in response: #if the player split, and has to play the second hand
            print("--- Moving to next split hand ---")
            continue

        if "ACTION" in response:
            continue

        if "ERROR" in response:
            print("unable to perform the action")
            continue

def login(clientSocket, user):
    #send a login request
    loginRequest = "LOGIN " + user
    clientSocket.send(loginRequest.encode())
    #expects a response in the form of "Login <balance>"
    loginResponse = clientSocket.recv(1024).decode()
    return loginResponse.split()[1]

def playGame(clientSocket, user):
    #sends start in the form: "BET <bet>"
    #verifies if the bet is valid or not
    while True:
        balance = login(clientSocket, user)
        print("Balance: " + balance)
        print("To exit, enter 'x'")
        bet = input("To begin, enter a bet: ")
        if bet == "x":
            return
        startRequest = "BET " + bet
        clientSocket.send(startRequest.encode())
        startResponse = clientSocket.recv(1024).decode().split()
        if "invalid" in startResponse:
            print("bet invalid")
            continue

        displayDealer(clientSocket)
        displayPlayer(clientSocket)


        if "RESULT" in startResponse:
            displayResult(startResponse)
            return  # round finished

        playHand(clientSocket)


def ClientMain():
    #Specify the IP address and port number of the server
    serverIP = 'localhost'
    serverPort = 12346
    #Create a while loop to support multiple times of service
    while True:
        #Create a client socket and connect it with the server
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))

        #Provide a menu for the users to choose their actions
        print("Welcome to Online Blackjack!")
        #accepts a username to login and retrieve the user's balance
        user = input("Enter a user name to get started:")

        print("Welcome "+ user + "!")
        playGame(clientSocket, user)

        clientSocket.close()


ClientMain()
