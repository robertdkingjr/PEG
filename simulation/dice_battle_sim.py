import random
import numpy as np
import pandas as pd

# =============================
# Configuration
# =============================
TRIALS = 10_000
MAX_DICE = 6
random.seed(42)

# =============================
# Dice utilities
# =============================

def roll_dice(n):
    """Roll n independent d6 dice."""
    return [random.randint(1, 6) for _ in range(n)]


def commit_dice(rolls):
    """
    Commit:
      - exactly one highest die (mandatory)
      - ALL additional dice that rolled 6
    Dice are values, but we carefully handle duplicates.
    """
    highest = max(rolls)

    # Mandatory commit
    committed = [highest]

    # Optional extras: all other 6s
    sixes = [r for r in rolls if r == 6]
    committed.extend(sixes[1:])

    return committed


# =============================
# Single battle simulation
# =============================

def simulate_battle(A, D):
    """
    Simulate one battle for A attack dice vs D defence dice

    Returns:
        dict: labelled results of simulation
    """

    # ---- Attacker commit (once) ----
    attackers_committed = []
    n_attacker_rolls = 0
    while len(attackers_committed) < A:
        n_attacker_rolls += 1
        attackers_rolled = roll_dice(A - len(attackers_committed))
        attackers_committed.extend(commit_dice(attackers_rolled))

    attackers = sorted(attackers_committed.copy(), reverse=True)
    defenders_committed = []
    n_attacker_killed = 0
    n_defender_killed = 0
    n_attacker_blocked = 0

    # ---- Defender defense loop ----
    n_defender_rolls = 0
    while attackers and n_defender_killed == 0:

        n_defender_rolls += 1
        defenders = sorted(roll_dice(D), reverse=True)

        defender_committed = False
        while defenders:
            if not attackers:
                break

            # take the next (highest) defender out of the reverse-sorted list
            d = defenders.pop(0)

            killable = [a for a in attackers if d > a]
            blockable = [a for a in attackers if d == a]

            # Prefer a kill if possible
            if killable:
                a = max(killable)
                attackers.remove(a)
                n_attacker_killed += 1
                defender_committed = True
                defenders_committed.append(d)

            # Use a block next if possible
            elif blockable:
                a = max(blockable)
                attackers.remove(a)
                n_attacker_blocked += 1
                defender_committed = True
                defenders_committed.append(d)

            # REROLL: Avoid losses if one has already been committed this roll
            elif defender_committed:
                n_defender_rolls += 1
                defenders = sorted(roll_dice(len(defenders) + 1), reverse=True)  # +1 includes d placed back in pool
                defender_committed = False

            # Forced defensive loss, take out the highest attacker in order
            else:
                a = attackers.pop(0)
                defender_committed = True
                defenders_committed.append(d)

                if d < a:
                    n_defender_killed += 1
                elif d > a:
                    n_attacker_killed += 1
                elif d == a:
                    n_attacker_blocked += 1
                else:
                    raise RuntimeError(f'Unhandled case: {a} {d}')

        # # Fully successful defense = NO defender losses
        # if d_kill == 0:
        #     continue
        # else:
        #     break
    data = {
        'A': A,
        'D': D,
        'AL': n_attacker_killed,
        'DL': n_defender_killed,
        'B': n_attacker_blocked,
        'ATTACK': attackers_committed,
        'DEFENSE': defenders_committed,
        'A_ROLLS': n_attacker_rolls,
        'D_ROLLS': n_defender_rolls,
    }

    return data

# =============================
# Monte Carlo table
# =============================

def run_monte_carlo(destination='battle_sim_results.csv'):

    results = []

    for A in range(1, MAX_DICE + 1):
        for D in range(1, MAX_DICE + 1):
            for t in range(TRIALS):
                if t % 1000 == 0:
                    print(f'Simulating {A}/{D}/{t}')

                results.append(simulate_battle(A, D))

            #     a_losses.append(al)
            #     d_losses.append(dl)
            #     nets.append(net)
            #
            # attacker_loss[A-1, D-1] = np.mean(a_losses)
            # defender_loss[A-1, D-1] = np.mean(d_losses)
            # net_adv[A-1, D-1] = np.mean(nets)

    df = pd.DataFrame(results)
    df.to_csv(destination)
    print(df.describe())

    # # =============================
    # # Display results
    # # =============================
    #
    # idx = [f"A{i}" for i in range(1, 7)]
    # cols = [f"D{i}" for i in range(1, 7)]
    #
    # print("\nATTACKER PEGS LOST (avg):")
    # print(pd.DataFrame(attacker_loss, index=idx, columns=cols).round(3))
    #
    # print("\nDEFENDER PEGS LOST (avg):")
    # print(pd.DataFrame(defender_loss, index=idx, columns=cols).round(3))
    #
    # print("\nNET ADVANTAGE (avg, bounded by committed attacker dice):")
    # print(pd.DataFrame(net_adv, index=idx, columns=cols).round(3))




if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    run_monte_carlo()
