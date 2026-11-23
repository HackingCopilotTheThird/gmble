import random

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