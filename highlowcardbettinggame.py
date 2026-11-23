import random

def start():
    STARTING_BANKROLL = 1000
    MIN_BET = 10
    HOUSE_EDGE = 0.05
    RESHUFFLE_BELOW = 10

    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    RANK_NAMES = {11: "Jack", 12: "Queen", 13: "King", 14: "Ace"}

    def card_name(card):
        r, s = card
        n = RANK_NAMES.get(r, str(r))
        return n + " of " + s

    def new_deck(exclude=None):
        deck = []
        for suit in SUITS:
            for rank in range(2, 15):
                card = (rank, suit)
                if card != exclude:
                    deck.append(card)
        random.shuffle(deck)
        return deck

    def clear_screen():
        print("\n" * 50)

    def show_rules():
        print("\n" + "=" * 46)
        print("                HOW TO PLAY")
        print("=" * 46)
        print("GOAL")
        print("  Guess if the next card is HIGHER or LOWER than")
        print("  the one showing. Start with $" + str(STARTING_BANKROLL) + " and grow it.")
        print()
        print("CARDS")
        print("  2 is lowest, Ace is highest (J=11, Q=12, K=13).")
        print("  Suits don't matter.")
        print()
        print("PAYOUTS")
        print("  Odds are based on the cards LEFT in the deck.")
        print("  Riskier bets pay more, safer bets pay less.")
        print("  Example: 2:1 means a $100 bet wins $200.")
        print("  A " + str(int(HOUSE_EDGE * 100)) + "% house edge is taken off every payout,")
        print("  and winning bets always pay at least 0.10:1.")
        print("  Winnings are rounded down to whole dollars")
        print("  (minimum win is $1).")
        print()
        print("PUSH (TIE)")
        print("  If the next card has the SAME rank, nobody wins")
        print("  or loses. Your bet is returned.")
        print()
        print("BETTING")
        print("  Min bet $" + str(MIN_BET) + ", max is your whole bankroll.")
        print("  Type 'all' to bet everything.")
        print("  You can't bet on an impossible outcome")
        print("  (Higher on an Ace, Lower on a 2).")
        print()
        print("GAME OVER")
        print("  The game ends if you quit or drop below $" + str(MIN_BET) + ".")
        print("  The deck reshuffles when fewer than " + str(RESHUFFLE_BELOW) + " cards")
        print("  remain.")
        print()
        print("TIPS")
        print("  * Safe bets grow slowly; one loss erases many wins.")
        print("  * Long shots can swing big but usually lose.")
        print("  * The house edge wins over time - play for fun")
        print("    and know when to cash out!")
        print()
        print("COMMANDS")
        print("  h = higher   l = lower   r = rules   q = quit")
        print("=" * 46)

    def calculate_odds(current_card, deck):
        curr_rank = current_card[0]
        total = len(deck)
        higher_count = 0
        lower_count = 0

        for rank, suit in deck:
            if rank > curr_rank:
                higher_count += 1
            elif rank < curr_rank:
                lower_count += 1

        return {
            "higher": make_odds(higher_count, total),
            "lower": make_odds(lower_count, total),
        }

    def make_odds(winning_cards, total_cards):
        if winning_cards == 0:
            return (0.0, 0.0)
        prob = winning_cards / total_cards
        fair_payout = (1 - prob) / prob
        payout = fair_payout * (1 - HOUSE_EDGE)
        payout = max(payout, 0.10)
        return (prob, payout)

    def describe_difficulty(prob):
        if prob >= 0.70:
            return "Safe"
        if prob >= 0.50:
            return "Fair"
        if prob >= 0.30:
            return "Risky"
        return "Long shot"

    def safe_input(prompt):
        try:
            return input(prompt).strip().lower()
        except:
            print()
            return "q"

    def get_choice(odds):
        while True:
            ans = safe_input("Your pick - (h)igher, (l)ower, (r)ules, (q)uit: ")

            if ans in ("h", "higher"):
                choice = "higher"
            elif ans in ("l", "lower"):
                choice = "lower"
            elif ans in ("r", "rules", "help", "?"):
                show_rules()
                continue
            elif ans in ("q", "quit", "exit"):
                return "quit"
            else:
                print("  Please type h, l, r, or q.")
                continue

            if odds[choice][0] == 0:
                print("  That bet is impossible - no card can beat that! Pick the other one.")
                continue
            return choice

    def get_bet(bankroll):
        max_bet = bankroll
        while True:
            text = safe_input("Bet amount ($" + str(MIN_BET) + "-$" + str(max_bet)
                          + ", 'all', 'r' for rules, 'q' to quit): ")

            if text in ("q", "quit", "exit"):
                return None
            if text in ("r", "rules", "help", "?"):
                show_rules()
                continue
            if text == "all":
                return max_bet

            text = text.replace("$", "").replace(",", "")
            if not text.isdigit():
                print("  Please enter a whole number (no decimals or negatives).")
                continue

            bet = int(text)
            if bet < MIN_BET:
                print("  Minimum bet is $" + str(MIN_BET) + ".")
            elif bet > bankroll:
                print("  You only have $" + str(bankroll) + ".")
            else:
                return bet

    def ask_yes_no(prompt):
        while True:
            answer = safe_input(prompt)
            if answer in ("y", "yes"):
                return True
            if answer in ("n", "no", "q"):
                return False
            print("  Please type y or n.")

    def show_odds(odds):
        print("\n  Bet        Chance    Payout    Difficulty")
        print("  " + "-" * 42)
        for choice in ("higher", "lower"):
            prob, payout = odds[choice]
            if prob == 0:
                print("  " + choice.capitalize().ljust(10) + " impossible")
            else:
                print("  " + choice.capitalize().ljust(10)
                  + (str(round(prob * 100)) + "%").ljust(10)
                  + (str(round(payout, 2)) + ":1").ljust(10)
                  + describe_difficulty(prob))
        print()

    def play_game():
        bankroll = STARTING_BANKROLL
        rounds = 0
        wins = 0
        biggest_bankroll = bankroll

        deck = new_deck()
        current_card = deck.pop()

        while True:
            if bankroll < MIN_BET:
                print("\nYou're out of money. GAME OVER!")
                break

            if len(deck) < RESHUFFLE_BELOW:
                print("\n  (Reshuffling the deck...)")
                deck = new_deck(exclude=current_card)

            print("\n" + "=" * 46)
            print("Bankroll: $" + str(bankroll) + "   |   Cards left: " + str(len(deck)))
            print("=" * 46)
            print("Current card:  >>> " + card_name(current_card) + " <<<")

            odds = calculate_odds(current_card, deck)
            show_odds(odds)

            choice = get_choice(odds)
            if choice == "quit":
                break

            bet = get_bet(bankroll)
            if bet is None:
                break

            next_card = deck.pop()
            rounds += 1
            print("\nDealing...  " + card_name(next_card) + "!")

            if next_card[0] == current_card[0]:
                print("Same rank - it's a PUSH. Your bet is returned.")
            else:
                went_higher = next_card[0] > current_card[0]
                player_won = (choice == "higher") == went_higher

                if player_won:
                    payout = odds[choice][1]
                    winnings = max(int(bet * payout), 1)
                    bankroll += winnings
                    wins += 1
                    print("YOU WIN! +$" + str(winnings))
                else:
                    bankroll -= bet
                    print("You lose. -$" + str(bet))

            biggest_bankroll = max(biggest_bankroll, bankroll)
            current_card = next_card

            if bankroll >= MIN_BET:
                ans = ""
                while ans != "a" and ans != "m":
                    ans = safe_input("\nWould you like to play (a)nother round or return to the (m)enu? ")
                    if ans == "q":
                        ans = "m"
                if ans == "m":
                    break

        print("\n" + "=" * 46)
        print("GAME SUMMARY")
        print("=" * 46)
        print("Rounds played:   " + str(rounds))
        print("Rounds won:      " + str(wins))
        print("Peak bankroll:   $" + str(biggest_bankroll))
        print("Final bankroll:  $" + str(bankroll))
        difference = bankroll - STARTING_BANKROLL
        if difference >= 0:
            print("Net result:      +$" + str(difference))
        else:
            print("Net result:      -$" + str(-difference))

    def highlowcardbettinggame():
        print("=" * 46)
        print("        HIGH-LOW CARD BETTING GAME")
        print("=" * 46)
        show_rules()
        print("\nTip: type 'r' at any prompt to see these rules again.")
        safe_input("Press Enter to start...")
        clear_screen()

        play_game()
        print("\nReturning to menu...")

    highlowcardbettinggame()