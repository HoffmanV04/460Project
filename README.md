# Black Jack Game
## Client:
Main():
  The client creates a connection on port 12346  
  When connected, it asks for a user name and passes it into playGame()  

playGame():  
  sends this message to the server: "LOGIN <user>"  
  if the user does not exist, create a user and initialize their balance to 100  
  server responds: "LOGIN <balance>"
  client displays the user's balance and asks for a bet amount  
  client send the bet message:  "BET <bet>"  
  server should verify the bet amount:  
  if the amount is invalid, return the message: "BET invalid"  
  - client should then ask for a new bet  
  if the amount is valid, the server will deal cards and tell the client what to do next  
  - client checks if the reponse was RESULT  
  - RESULT <result_message> means that the game already finished (in this case, the player was dealt blackjack and won)  
  - else, call playHand()  

playHand()  
   tells user to enter a  number associated with a choice  
   - (1) HIT  
   - (2) STAND  
   - (3) DOUBLE  
   - (4) SPLIT  
   send this as a message to the server, which would update the hand and scores, and respond with what the user should do next.  
   the client would request to view their hand and the dealer's by calling displayDealer(), or displayPlayer()  
   then it checks the reponse with the expected messages:  
   - RESULT - means the game has finished  
   - NEXT_HAND - if the user split their hand, then must now play the next hand  
   - ACTION - means that the user must choose to hit or stand considering the new card  
   - ERROR - if the action cannot be performed, like if they try to split or double when not allowed  

displayPlayer()  
  gets the user's hand and value of the hand  
  send message to the server: "GET player"  
  server responds with the message: "PLAYER <value> <card1> <card2>..."  
  then displays this data  

displayDealer()  
  same code as in the displayPlayer, but send the message: "GET dealer"  
  and expects the response: "DEALER <value> <card1> <card2>..."  

displayResult()  
  server woulds send the result message in the form: "RESULT <message>"  
  the message part could be   
  win: "player_blackjack", "player_win", "dealer_bust"  
  lose: "dealer_win", "player_bust", "dealer_blackjack"  
  or "push", which is a draw
  
