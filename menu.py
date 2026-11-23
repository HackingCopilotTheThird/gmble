import sys
import random

import poker
import numberguessing
import highlowcardbettinggame

OPTIONS = [
    ("Play Poker: ", poker.start),
    ("Play Number Guessing Game: ", numberguessing.start),
    ("Play High-Lo: ", highlowcardbettinggame.start),
    ("Exit: ", None),
]
def clear_screen():
    print("\033[2J\033[H", end=", flush=True") #ansi code; it clears the screen 

def get_key():
    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):          
            return {"H": "up", "P": "down"}.get(msvcrt.getwch(), "")
        if ch == "\r":
            return "enter"
        if ch == "\x03":
            raise KeyboardInterrupt
        return ch
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":                
                if sys.stdin.read(1) == "[":
                    return {"A": "up", "B": "down"}.get(sys.stdin.read(1), "")
                return ""
            if ch in ("\r", "\n"):
                return "enter"
            if ch == "\x03":
                raise KeyboardInterrupt
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def draw_menu(selected):
    clear_screen()
    print("\033[1;36m========= Main Menu =========\033[0m\n")
    for i, (label, _) in enumerate(OPTIONS):
        if i == selected:
            print("  \033[7m > " + label + " \033[0m")
        else:
            print("    " + label)
    print("\n  Use \u2191/\u2193 to move, Enter to select")


def arrow_menu():
    selected = 0
    while True:
        draw_menu(selected)
        key = get_key()
        if key in ("up", "w", "k"):
            selected = (selected - 1) % len(OPTIONS)
        elif key in ("down", "s", "j"):
            selected = (selected + 1) % len(OPTIONS)
        elif key.isdigit() and 1 <= int(key) <= len(OPTIONS):
            return int(key) - 1            
        elif key == "enter":
            return selected


def text_menu():
    while True:
        print("\n========= Main Menu =========")
        for i, (label, _) in enumerate(OPTIONS):
            print(str(i + 1) + ". " + label)
        choice = input("Choose (1-" + str(len(OPTIONS)) + "): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(OPTIONS):
            return int(choice) - 1
        print("Invalid choice")


def main():
    try:
        while True:
            index = arrow_menu() if sys.stdin.isatty() else text_menu()
            label, action = OPTIONS[index]

            clear_screen()
            if action is None:
                break
            action()
            input("\nPress Enter to return to the menu...")
    except KeyboardInterrupt:
        print()
    print("Thanks for playing")


if __name__ == "__main__":
    main()


def start():
    RANK_VALUES = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
        "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14,
    }

    SUIT_SYMBOLS = {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}

    HAND_NAMES = {
        8: "Straight Flush",
        7: "Four of a Kind",
        6: "Full House",
        5: "Flush",
        4: "Straight",
        3: "Three of a Kind",
        2: "Two Pair",
        1: "One Pair",
        0: "High Card",
    }

    STARTING_CHIPS = 100
    ANTE = 5


    def make_deck():
        deck = []
        for r in RANK_VALUES:
            for s in SUIT_SYMBOLS:
                deck.append(r + s)
        return deck


    def deal(deck, n):
        out = []
        for _ in range(n):
            out.append(deck.pop())
        return out


    def pretty(card):
        r = card[0]
        s = card[1]
        if r == "T":
            r = "10"
        return r + SUIT_SYMBOLS[s]

    def show_hand(hand, numbered=False):
        out = ""
        for i in range(len(hand)):
            if numbered:
                out += "[" + str(i + 1) + "] "
            out += pretty(hand[i]) + "   "
        return out


    def evaluate(hand):
        tally = {}
        for card in hand:
            v = RANK_VALUES[card[0]]
            if v in tally:
                tally[v] += 1
            else:
                tally[v] = 1

        combos = []
        for v in tally:
            combos.append((tally[v], v))
        combos.sort(reverse=True)

        vals = []
        for c in combos:
            vals.append(c[1])

        suits = {}
        for card in hand:
            suits[card[1]] = True
        flush = len(suits) == 1

        srt = sorted(vals)
        straight = False
        if len(srt) == 5:
            if srt[4] - srt[0] == 4:
                straight = True
            elif srt == [2, 3, 4, 5, 14]:  # wheel
                straight = True
                vals = [5, 4, 3, 2, 1]

        top = combos[0][0]
        if straight and flush:
            power = 8
        elif top == 4:
            power = 7
        elif top == 3 and len(combos) == 2:
            power = 6
        elif flush:
            power = 5
        elif straight:
            power = 4
        elif top == 3:
            power = 3
        elif top == 2 and len(combos) == 3:
            power = 2
        elif top == 2:
            power = 1
        else:
            power = 0

        return power, vals


    def player_discard(hand, deck):
        print("\nYour hand:  " + show_hand(hand, numbered=True))
        ans = input("Which cards to swap? (e.g. 1 3 5, or press Enter to keep all): ")

        picks = []
        for w in ans.split():
            if w.isdigit():
                n = int(w)
                if 1 <= n <= 5 and (n - 1) not in picks:
                    picks.append(n - 1)

        for i in picks:
            hand[i] = deck.pop()

        print("You swapped " + str(len(picks)) + " card(s).")
        return hand


    def computer_discard(hand, deck):
        tally = {}
        for card in hand:
            tally[card[0]] = tally.get(card[0], 0) + 1

        n = 0
        for i in range(len(hand)):
            if tally[hand[i][0]] == 1:
                hand[i] = deck.pop()
                n += 1

        print("Computer swapped " + str(n) + " card(s).")
        return hand


    def ask_number(prompt, lo, hi):
        while True:
            ans = input(prompt)
            if ans.isdigit():
                n = int(ans)
                if lo <= n <= hi:
                    return n
            print("Please enter a number from " + str(lo) + " to " + str(hi) + ".")


    def computer_bet_amount(power, cap):
        if power >= 3:
            amt = random.randint(10, 20)
        elif power >= 1:
            amt = random.randint(5, 10)
        elif random.randint(1, 5) == 1:
            amt = random.randint(5, 10)
        else:
            amt = 0
        if amt > cap:
            amt = cap
        return amt


    def computer_calls(power, bet):
        if power >= 2:
            return True
        if power == 1:
            return bet <= 15 or random.randint(1, 2) == 1
        return bet <= 5 or random.randint(1, 4) == 1


    def betting_round(bank, pot, cpu_power, stage):
        print("\n--- Betting: " + stage + " ---")
        print("Pot: " + str(pot) + " | You: " + str(bank["player"]) +
              " chips | Computer: " + str(bank["computer"]) + " chips")

        cap = min(bank["player"], bank["computer"])
        if cap == 0:
            print("Someone is all-in. No more betting.")
            return pot, None

        pick = ""
        while pick != "c" and pick != "b":
            pick = input("(c)heck or (b)et? ").lower()

        if pick == "b":
            bet = ask_number("How much? (1-" + str(cap) + "): ", 1, cap)
            bank["player"] -= bet
            pot += bet
            print("You bet " + str(bet) + ".")

            if computer_calls(cpu_power, bet):
                bank["computer"] -= bet
                pot += bet
                print("Computer calls.")
            else:
                print("Computer folds!")
                return pot, "computer"
        else:
            print("You check.")
            bet = computer_bet_amount(cpu_power, cap)
            if bet == 0:
                print("Computer checks.")
            else:
                bank["computer"] -= bet
                pot += bet
                print("Computer bets " + str(bet) + ".")
                move = ""
                while move != "c" and move != "f":
                    move = input("(c)all or (f)old? ").lower()
                if move == "c":
                    bank["player"] -= bet
                    pot += bet
                    print("You call.")
                else:
                    print("You fold.")
                    return pot, "player"

        return pot, None


    def play_round(bank):
        deck = make_deck()
        random.shuffle(deck)

        ante = min(ANTE, bank["player"], bank["computer"])
        bank["player"] -= ante
        bank["computer"] -= ante
        pot = ante * 2
        print("\nBoth players ante " + str(ante) + " chip(s).")

        me = deal(deck, 5)
        cpu = deal(deck, 5)

        print("\nYour hand:  " + show_hand(me))
        cpu_power, cpu_tb = evaluate(cpu)
        pot, quitter = betting_round(bank, pot, cpu_power, "before the draw")
        if quitter != None:
            winner = "player" if quitter == "computer" else "computer"
            bank[winner] += pot
            print("\n" + winner.capitalize() + " wins the pot of " + str(pot) + "!")
            return

        me = player_discard(me, deck)
        cpu = computer_discard(cpu, deck)

        cpu_power, cpu_tb = evaluate(cpu)
        print("\nYour new hand:  " + show_hand(me))
        pot, quitter = betting_round(bank, pot, cpu_power, "after the draw")
        if quitter != None:
            winner = "player" if quitter == "computer" else "computer"
            bank[winner] += pot
            print("\n" + winner.capitalize() + " wins the pot of " + str(pot) + "!")
            return

        my_power, my_tb = evaluate(me)

        print("\n" + "=" * 40)
        print("SHOWDOWN   (pot: " + str(pot) + ")")
        print("=" * 40)
        print("You:       " + show_hand(me))
        print("           -> " + HAND_NAMES[my_power])
        print("Computer:  " + show_hand(cpu))
        print("           -> " + HAND_NAMES[cpu_power])
        print("=" * 40)

        if (my_power, my_tb) > (cpu_power, cpu_tb):
            bank["player"] += pot
            print("You win " + str(pot) + " chips!")
        elif (my_power, my_tb) < (cpu_power, cpu_tb):
            bank["computer"] += pot
            print("Computer wins " + str(pot) + " chips.")
        else:
            bank["player"] += pot // 2
            bank["computer"] += pot // 2
            print("It's a tie! The pot is split.")


    def poker():
        print("Welcome to 5-Card Draw Poker with chips!")
        print("Everyone starts with " + str(STARTING_CHIPS) + " chips. Ante is " + str(ANTE) + ".")

        bank = {"player": STARTING_CHIPS, "computer": STARTING_CHIPS}

        going = True
        while going:
            play_round(bank)

            print("\nChips -> You: " + str(bank["player"]) +
                  " | Computer: " + str(bank["computer"]))

            if bank["player"] == 0:
                print("You're out of chips. Game over!")
                going = False
            elif bank["computer"] == 0:
                print("The computer is out of chips. You win the game!")
                going = False
            else:
                ans = ""
                while ans != "a" and ans != "m":
                    ans = input("\nWould you like to play (a)nother round or return to the (m)enu? ").strip().lower()
                if ans == "m":
                    going = False

        print("Returning to menu...")


    poker()

def start():
    STARTING_COINS = 2500
    MAX_GUESSES = 10
    MAX_NUMBER = 500
    WIN_STREAK_FOR_BONUS = 3
    LOSS_STREAK_FOR_PENALTY = 3
    BONUS_PERCENT = 10
    PENALTY_PERCENT = 10


    def new_game():
        st = {
            "coins": STARTING_COINS,
            "win_streak": 0,
            "loss_streak": 0,
            "rounds_played": 0,
            "rounds_won": 0,
            "used_numbers": [],
        }
        return st


    def random_number(state):
        used = state["used_numbers"]

        if len(used) >= MAX_NUMBER:
            used.clear()

        available = [n for n in range(1, MAX_NUMBER + 1) if n not in used]

        secret = random.choice(available)
        used.append(secret)
        return secret


    def get_bet(coins):
        while True: # fix infinite loop if user spams inputs, whatever works for now
            text = input("Enter your bet (1-" + str(coins) + ") or 'q' to quit: ").strip().lower()

            if text == "q":
                return 0
            if not text.isdigit():
                print("Please enter a whole number.")
                continue

            bet = int(text)
            if bet < 1 or bet > coins:
                print("Your bet must be between 1 and " + str(coins) + ".")
                continue

            return bet


    def get_hint(guess, secret):
        distance = abs(guess - secret)

        if distance <= 10:
            return "Burning hot! (You are within 10 places of this number)"
        elif distance <= 40:
            return "Warm (You are within 40 places of this number)"
        elif distance <= 100:
            return "Cold (You are within 100 places of this number)"
        else:
            return "Freezing! (Sorry, please guess better)"


    def get_guess():
        while True:
            text = input("Your guess (1-" + str(MAX_NUMBER) + "): ").strip()
            if text.isdigit():
                guess = int(text)
                if 1 <= guess <= MAX_NUMBER:
                    return guess
            print("Please enter a whole number from 1 to " + str(MAX_NUMBER) + ".")


    def play_guessing_phase(secret):
        for attempt in range(1, MAX_GUESSES + 1):
            print("\nGuess " + str(attempt) + " of " + str(MAX_GUESSES))
            guess = get_guess()

            if guess == secret:
                print("Correct! The number was " + str(secret) + "!")
                return True
            else:
                print(get_hint(guess, secret))

        print("\nOut of guesses! The number was " + str(secret) + ".")
        return False


    def handle_win(state, bet):
        payout = bet * 2
        state["win_streak"] += 1
        state["loss_streak"] = 0
        state["rounds_won"] += 1

        print("You win! You get " + str(payout) + " coins back (bet doubled).")

        if state["win_streak"] == WIN_STREAK_FOR_BONUS:
            bonus = payout * BONUS_PERCENT // 100
            payout = payout + bonus
            print("3 wins in a row! Bonus of " + str(bonus) + " coins (+" + str(BONUS_PERCENT) + "%)!")
            state["win_streak"] = 0

        state["coins"] += payout


    def handle_loss(state, bet):
        state["loss_streak"] += 1
        state["win_streak"] = 0

        print("You lost your bet of " + str(bet) + " coins.")

        if state["loss_streak"] >= LOSS_STREAK_FOR_PENALTY:
            penalty = (bet * PENALTY_PERCENT + 99) // 100
            if penalty > state["coins"]:
                penalty = state["coins"]
            state["coins"] -= penalty
            print(str(state["loss_streak"]) + " losses in a row! Extra penalty of "
                  + str(penalty) + " coins (" + str(PENALTY_PERCENT) + "% of your bet).")


    def play_round(state):
        print("\n" + "=" * 40)
        print("Coins: " + str(state["coins"]))
        print("Win streak: " + str(state["win_streak"]) + " | Loss streak: " + str(state["loss_streak"]))
        print("=" * 40)

        bet = get_bet(state["coins"])
        if bet == 0:
            return False

        state["coins"] -= bet
        state["rounds_played"] += 1

        secret = random_number(state)
        print("\nI'm thinking of a number from 1 to " + str(MAX_NUMBER) + "...")

        won = play_guessing_phase(secret)

        if won:
            handle_win(state, bet)
        else:
            handle_loss(state, bet)

        return True


    def show_summary(state):
        print("\n" + "=" * 40)
        print("GAME OVER")
        print("Final coins: " + str(state["coins"]))
        print("Rounds played: " + str(state["rounds_played"]))
        print("Rounds won: " + str(state["rounds_won"]))
        if state["coins"] > STARTING_COINS:
            print("You finished with a profit. Nice!")
        elif state["coins"] == STARTING_COINS:
            print("You broke even.")
        else:
            print("You finished down. Better luck next time!")
        print("=" * 40)


    def numberguessing():
        print("Welcome to the Number Guessing Bet Game!")
        print("You start with " + str(STARTING_COINS) + " coins.")
        print("Bet coins, then guess a number from 1-" + str(MAX_NUMBER) + " in " + str(MAX_GUESSES) + " tries.")
        print("Win: bet doubled back. 3 wins in a row: +10% bonus.")
        print("Lose: bet is gone. 3 losses in a row (" + str(3 * MAX_GUESSES) + " failed tries): extra 10% penalty on each further loss.")

        state = new_game()

        while True:
            if state["coins"] <= 0:
                print("\nYou're out of coins!")
                break

            keep_playing = play_round(state)
            if not keep_playing:
                break

            if state["coins"] > 0:
                ans = ""
                while ans != "a" and ans != "m":
                    ans = input("\nWould you like to play (a)nother round or return to the (m)enu? ").strip().lower()
                if ans == "m":
                    break

        show_summary(state)
        print("Returning to menu...")


    numberguessing()

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