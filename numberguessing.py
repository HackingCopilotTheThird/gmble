import random

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


    def main():
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


    main()