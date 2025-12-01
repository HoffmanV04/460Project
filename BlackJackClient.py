from socket import *

def resultMessage(game_result):
    wins = ["player_blackjack", "player_win", "dealer_bust"]
    loses = ["dealer_win", "player_bust", "dealer_blackjack"]
    
    if game_result.lower() in wins:
        print("You Win!" + game_result)
    elif game_result.lower() in loses:
        print("Dealer Wins! " + game_result)
    elif game_result.lower() == "push":
        print("Push, no winner")

def displayResult(result):
    #expects result in form of "RESULT <game_result1> <game_result2>
    print("Results:")
    resultMessage(result[1])
    if len(result) > 2:
        print("Second Hand:")
        resultMessage(result[2])
    return


def displayHand(clientSocket, person):
    #takes the argument of whose hand you want to retrieve
    handRequest = "GET " + person
    clientSocket.send(handRequest.encode())
    #expects response in form "HAND <value> <card1> <card2> ..."

    handResponse = clientSocket.recv(1024).decode()
    if "HAND" in handResponse:
        hand=handResponse.split()
        # initialize  hand and the value of it
        hand.pop(0)
        value = hand.pop(0)
    
        if person == "player":
            display_hand = "Your Hand: "
        else:
            display_hand = "Dealer's Hand: "
        #Player's  card:
        for card in hand:
            display_hand += card + " "
        #print the player's hand
        print("--------------------------------")
        print(display_hand)
        #Total of the hand
        print("Your Total: " + value + "\n")
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

        print("before response")
        actionResponse = clientSocket.recv(1024).decode()
        response = actionResponse.split()
        print(f"After response: {response}")

        #view updated hands
        displayHand(clientSocket, "dealer")
        displayHand(clientSocket, "player")

        #the next step
        if "RESULT" in response: #when the game ends and returns the result
            displayResult(response)
            return
        elif "NEXT_HAND" in response: #if the player split, and has to play the second hand
            print("--- Moving to next split hand ---")
            continue
        elif "ACTION" in response:
            continue
        elif "ERROR" in response:
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

        displayHand(clientSocket, "dealer")
        displayHand(clientSocket, "player")

        


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
