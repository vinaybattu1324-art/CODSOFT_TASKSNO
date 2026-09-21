import random

CHOICES = {
    "1": "rock",
    "2": "paper",
    "3": "scissors",
}

BEATS = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock",
}
EMOJI = {
    "rock": "\U0001FAA8",
    "paper": "\U0001F4C4",
    "scissors": "\u2702\ufe0f",
}

def get_user_choice():
    """Show the menu and return the player's choice as a lowercase string."""
    print("\nMake your move:")
    for key, name in CHOICES.items():
        print(f"  {key}. {name.capitalize()}")
    while True:
        choice = input("Enter choice (1-3): ").strip()
        if choice in CHOICES:
            return CHOICES[choice]
        print("Please enter 1, 2, or 3.")

def get_computer_choice():
    """Randomly pick rock, paper, or scissors for the computer."""
    return random.choice(list(CHOICES.values()))

def determine_winner(user, computer):
    """Return 'user', 'computer', or 'tie' based on the game rules."""
    if user == computer:
        return "tie"
    if BEATS[user] == computer:
        return "user"
    return "computer"

def display_round(user, computer, winner):
    print(f"\nYou chose:      {user.capitalize()} {EMOJI[user]}")
    print(f"Computer chose: {computer.capitalize()} {EMOJI[computer]}")

    if winner == "tie":
        print("\nIt's a tie!")
    elif winner == "user":
        print(f"\nYou win! {user.capitalize()} beats {computer.capitalize()}.")
    else:
        print(f"\nComputer wins! {computer.capitalize()} beats {user.capitalize()}.")

def display_scoreboard(user_score, computer_score, ties, round_num):
    print("\n" + "-" * 34)
    print(f"  Scoreboard after round {round_num}")
    print(f"  You: {user_score}   Computer: {computer_score}   Ties: {ties}")
    print("-" * 34)

def ask_play_again():
    while True:
        again = input("\nPlay another round? [y/N]: ").strip().lower()
        if again in ("y", "yes"):
            return True
        if again in ("n", "no", ""):
            return False
        print("Please answer y or n.")

def main():
    print("=== Rock, Paper, Scissors ===")
    print("Rock beats Scissors, Scissors beats Paper, Paper beats Rock.")

    user_score = 0
    computer_score = 0
    ties = 0
    round_num = 0

    while True:
        round_num += 1
        print(f"\n--- Round {round_num} ---")

        user_choice = get_user_choice()
        computer_choice = get_computer_choice()
        winner = determine_winner(user_choice, computer_choice)

        display_round(user_choice, computer_choice, winner)

        if winner == "user":
            user_score += 1
        elif winner == "computer":
            computer_score += 1
        else:
            ties += 1

        display_scoreboard(user_score, computer_score, ties, round_num)

        if not ask_play_again():
            break

    print("\n=== Final Score ===")
    print(f"You: {user_score}   Computer: {computer_score}   Ties: {ties}")
    if user_score > computer_score:
        print("Congratulations, you won overall! \U0001F3C6")
    elif computer_score > user_score:
        print("The computer won overall. Better luck next time!")
    else:
        print("Overall, it's a tie!")
    print("\nThanks for playing!")

if __name__ == "__main__":
    main()