# greyhound_statistics

Exploring greyhound betting markets at face level.

## Data Source

Betfair publishes daily rundown of greyhound markets with valuable data [(betfair-sp)](https://promo.betfair.com/betfairsp/)
. This data is layed out as follows:

### Raw Schema
```
Field               Description
EVENT_ID            Betfair internal event ID
MENU_HINT           Contains the name of the race meeting
EVENT_NAME          The race name as it appears on the Betfair menu — place markets are always 'To Be Placed'
EVENT_DT            The start time of the race
SELECTION_ID        Betfair internal selection ID
SELECTION_NAME      The name of the runner
WIN_LOSE            1 if the runner won (or placed), 0 if it lost (or was unplaced)
BSP                 Betfair Starting Price
PPWAP               Weighted Average Price of all bets placed pre-off
MORNINGWAP          Weighted Average Price of all bets placed before 11am GMT
PPMAX               Maximum price placed before the off (only bets of a payout of more than GBP100 included)
PPMIN               Minimum price placed before the off (only bets of a payout of more than GBP100 included)
IPMAX               Maximum price placed in-play (only bets of a payout of more than GBP100 included)
IPMIN               Minimum price placed in-play (only bets of a payout of more than GBP100 included)
MORNINGTRADEDVOL    Amount traded before 11am GMT
PPTRADEDVOL         Amount traded before the off
IPTRADEDVOL         Amount traded in-play
```

Although some data in this is not accurate/given so it can be boggled down to a simpler format:

### Working Schema
```
Field               Description
EVENT_ID            Betfair internal event ID
MENU_HINT           Contains the name of the race meeting
EVENT_NAME          The race name as it appears on the Betfair menu - place markets are always 'To Be Placed'
EVENT_DT            The start time of the race given as dd-mm-yyyy hh:mm
SELECTION_ID        Betfair internal selection ID
SELECTION_NAME      The name of the runner
WIN_LOSE            1 if the runner won (or placed), 0 if it lost (or was unplaced)
BSP                 Betfair Starting Price
MORNINGTRADEDVOL    Amount traded before 11am GMT
PPTRADEDVOL         Amount traded before the off
```
