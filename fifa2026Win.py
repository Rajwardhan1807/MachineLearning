import math
import random
from typing import List, Dict, Tuple, Optional

# --- TEAM DATA & RATINGS (Based on recent FIFA / Elo ratings) ---
# Ratings roughly represent team strength. Higher means better chances.
TEAMS_DATA = {
    # Group A
    "USA": {"rating": 1660, "group": "A"},
    "Colombia": {"rating": 1750, "group": "A"},
    "Poland": {"rating": 1530, "group": "A"},
    "Iraq": {"rating": 1370, "group": "A"},
    
    # Group B
    "Canada": {"rating": 1460, "group": "B"},
    "Italy": {"rating": 1760, "group": "B"},
    "Ecuador": {"rating": 1570, "group": "B"},
    "Mali": {"rating": 1380, "group": "B"},
    
    # Group C
    "Mexico": {"rating": 1650, "group": "C"},
    "Germany": {"rating": 1730, "group": "C"},
    "Sweden": {"rating": 1550, "group": "C"},
    "Qatar": {"rating": 1400, "group": "C"},
    
    # Group D
    "Argentina": {"rating": 1860, "group": "D"},
    "Switzerland": {"rating": 1620, "group": "D"},
    "Egypt": {"rating": 1510, "group": "D"},
    "Uzbekistan": {"rating": 1360, "group": "D"},
    
    # Group E
    "France": {"rating": 1850, "group": "E"},
    "Croatia": {"rating": 1720, "group": "E"},
    "Nigeria": {"rating": 1490, "group": "E"},
    "Saudi Arabia": {"rating": 1430, "group": "E"},
    
    # Group F
    "Spain": {"rating": 1840, "group": "F"},
    "Morocco": {"rating": 1680, "group": "F"},
    "Ukraine": {"rating": 1580, "group": "F"},
    "Panama": {"rating": 1410, "group": "F"},
    
    # Group G
    "England": {"rating": 1810, "group": "G"},
    "Japan": {"rating": 1640, "group": "G"},
    "Ivory Coast": {"rating": 1500, "group": "G"},
    "Costa Rica": {"rating": 1420, "group": "G"},
    
    # Group H
    "Brazil": {"rating": 1800, "group": "H"},
    "South Korea": {"rating": 1600, "group": "H"},
    "Denmark": {"rating": 1520, "group": "H"},
    "Jamaica": {"rating": 1350, "group": "H"},
    
    # Group I
    "Belgium": {"rating": 1790, "group": "I"},
    "Australia": {"rating": 1590, "group": "I"},
    "Turkey": {"rating": 1540, "group": "I"},
    "Cameroon": {"rating": 1390, "group": "I"},
    
    # Group J
    "Netherlands": {"rating": 1780, "group": "J"},
    "Iran": {"rating": 1610, "group": "J"},
    "Chile": {"rating": 1440, "group": "J"},
    "South Africa": {"rating": 1340, "group": "J"},
    
    # Group K
    "Portugal": {"rating": 1770, "group": "K"},
    "Uruguay": {"rating": 1740, "group": "K"},
    "Austria": {"rating": 1560, "group": "K"},
    "Tunisia": {"rating": 1480, "group": "K"},
    
    # Group L
    "Senegal": {"rating": 1630, "group": "L"},
    "Algeria": {"rating": 1470, "group": "L"},
    "Peru": {"rating": 1450, "group": "L"},
    "New Zealand": {"rating": 1300, "group": "L"}
}

class Team:
    def __init__(self, name: str, rating: float, group: str):
        self.name = name
        self.rating = rating
        self.group = group
        self.reset_stats()
        
    def reset_stats(self):
        self.points = 0
        self.goals_for = 0
        self.goals_against = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    def __repr__(self):
        return f"{self.name} ({self.rating})"



def simulate_poisson(lmbda: float) -> int:
    """Generates a random number of goals using the Poisson distribution."""
    L = math.exp(-lmbda)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1

def simulate_match(team1: Team, team2: Team, is_knockout: bool = False) -> Tuple[int, int, Optional[str]]:
    """
    Simulates a match between two teams based on their rating differences.
    Returns: (team1_goals, team2_goals, winner_name_if_knockout)
    """
    r_ratio = team1.rating / team2.rating
    

    lmbda1 = 1.35 * (r_ratio ** 1.8)
    lmbda2 = 1.35 * ((1.0 / r_ratio) ** 1.8)
    

    goals1 = simulate_poisson(lmbda1)
    goals2 = simulate_poisson(lmbda2)
    
    if not is_knockout:
        return goals1, goals2, None
        
    # If it is a knockout match, we must have a winner.
    if goals1 > goals2:
        return goals1, goals2, team1.name
    elif goals2 > goals1:
        return goals1, goals2, team2.name
        
    # Simulate Extra Time (30 mins -> 1/3 of regular match expectation)
    et_lmbda1 = lmbda1 / 3.0
    et_lmbda2 = lmbda2 / 3.0
    et_goals1 = simulate_poisson(et_lmbda1)
    et_goals2 = simulate_poisson(et_lmbda2)
    
    total_goals1 = goals1 + et_goals1
    total_goals2 = goals2 + et_goals2
    
    if total_goals1 > total_goals2:
        return total_goals1, total_goals2, team1.name
    elif total_goals2 > total_goals1:
        return total_goals1, total_goals2, team2.name
        
    # Still tied -> Penalty Shootout (slightly favors the higher-rated team)
    t1_pen_prob = 0.5 + 0.1 * ((team1.rating - team2.rating) / 400.0)
    t1_pen_prob = max(0.3, min(0.7, t1_pen_prob))
    
    if random.random() < t1_pen_prob:
        return total_goals1, total_goals2, team1.name
    else:
        return total_goals1, total_goals2, team2.name


# --- TOURNAMENT SIMULATION CLASS ---
class WorldCupSimulation:
    def __init__(self, teams_dict: Dict[str, Dict]):
        self.teams = {name: Team(name, data["rating"], data["group"]) for name, data in teams_dict.items()}
        self.groups = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]

    def reset(self):
        for team in self.teams.values():
            team.reset_stats()

    def simulate_group_stage(self, verbose: bool = False) -> List[Team]:
        """
        Simulates the group stage where 48 teams are divided into 12 groups of 4.
        Returns the list of 32 teams that advance.
        """
        group_teams: Dict[str, List[Team]] = {g: [] for g in self.groups}
        for team in self.teams.values():
            group_teams[team.group].append(team)
            
        advancing_teams: List[Team] = []
        third_placed_teams: List[Team] = []

        for g in self.groups:
            teams_in_group = group_teams[g]
            # Play round-robin matches
            for i in range(len(teams_in_group)):
                for j in range(i + 1, len(teams_in_group)):
                    t1, t2 = teams_in_group[i], teams_in_group[j]
                    g1, g2, _ = simulate_match(t1, t2, is_knockout=False)
                    
                    # Update stats
                    t1.goals_for += g1
                    t1.goals_against += g2
                    t2.goals_for += g2
                    t2.goals_against += g1
                    
                    if g1 > g2:
                        t1.points += 3
                        t1.wins += 1
                        t2.losses += 1
                    elif g2 > g1:
                        t2.points += 3
                        t2.wins += 1
                        t1.losses += 1
                    else:
                        t1.points += 1
                        t2.points += 1
                        t1.draws += 1
                        t2.draws += 1
                        
                    if verbose:
                        print(f"Group {g}: {t1.name} {g1} - {g2} {t2.name}")

            # Sort group: 1) Points, 2) Goal Diff, 3) Goals For, 4) Rating (as final tie-breaker)
            teams_in_group.sort(key=lambda t: (t.points, t.goal_difference, t.goals_for, t.rating), reverse=True)
            
            # Top 2 advance automatically
            advancing_teams.append(teams_in_group[0])
            advancing_teams.append(teams_in_group[1])
            # Third-placed team enters comparison pool
            third_placed_teams.append(teams_in_group[2])

        # Rank third-placed teams: top 8 of 12 advance
        third_placed_teams.sort(key=lambda t: (t.points, t.goal_difference, t.goals_for, t.rating), reverse=True)
        for k in range(8):
            advancing_teams.append(third_placed_teams[k])

        if verbose:
            print("\n--- ADVANCING TEAMS FROM GROUP STAGE ---")
            for idx, team in enumerate(advancing_teams, 1):
                print(f"{idx}. {team.name} (Group {team.group})")
            print("----------------------------------------\n")

        return advancing_teams

    def simulate_tournament(self, verbose: bool = False) -> Dict[str, Team]:
        """Runs one full tournament simulation and returns results."""
        self.reset()
        qualifiers = self.simulate_group_stage(verbose)
        
        current_round = list(qualifiers)
        # Seed/pair them: to avoid adjacent group rematches, we shuffle once at Round of 32
        random.shuffle(current_round)
        
        stages = ["R32", "R16", "QF", "SF"]
        losers: Dict[str, List[Team]] = {stage: [] for stage in stages}
        
        for stage in stages:
            next_round = []
            if verbose:
                print(f"\n--- {stage} MATCHES ---")
            for i in range(0, len(current_round), 2):
                t1, t2 = current_round[i], current_round[i+1]
                g1, g2, winner_name = simulate_match(t1, t2, is_knockout=True)
                winner = t1 if winner_name == t1.name else t2
                loser = t2 if winner_name == t1.name else t1
                
                next_round.append(winner)
                losers[stage].append(loser)
                
                if verbose:
                    penalty_str = " (ET/Pens)" if g1 == g2 else ""
                    print(f"{t1.name} {g1} - {g2} {t2.name} -> {winner.name}{penalty_str}")
            current_round = next_round

        # Now current_round has 2 teams (Finalists), losers["SF"] has 2 teams (Third-place play-off)
        sf_loser1, sf_loser2 = losers["SF"][0], losers["SF"][1]
        f1, f2 = current_round[0], current_round[1]
        
        if verbose:
            print("\n--- THIRD PLACE PLAY-OFF ---")
        g1_3rd, g2_3rd, winner_3rd_name = simulate_match(sf_loser1, sf_loser2, is_knockout=True)
        third_place = sf_loser1 if winner_3rd_name == sf_loser1.name else sf_loser2
        fourth_place = sf_loser2 if winner_3rd_name == sf_loser1.name else sf_loser1
        if verbose:
            print(f"{sf_loser1.name} {g1_3rd} - {g2_3rd} {sf_loser2.name} -> Third Place: {third_place.name}")
            
        if verbose:
            print("\n--- THE FINAL ---")
        g1_f, g2_f, winner_f_name = simulate_match(f1, f2, is_knockout=True)
        winner = f1 if winner_f_name == f1.name else f2
        runner_up = f2 if winner_f_name == f1.name else f1
        if verbose:
            penalty_str = " (ET/Pens)" if g1_f == g2_f else ""
            print(f"  FINAL: {f1.name} {g1_f} - {g2_f} {f2.name} -> WINNER: {winner.name}{penalty_str}  \n")
            
        return {
            "winner": winner,
            "runner_up": runner_up,
            "third": third_place,
            "fourth": fourth_place,
            "sf_losers": losers["SF"],
            "qf_losers": losers["QF"],
            "r16_losers": losers["R16"],
            "r32_losers": losers["R32"]
        }


# --- MONTE CARLO SIMULATOR ---
def run_monte_carlo(sim: WorldCupSimulation, num_simulations: int = 5000):
    print(f"Running {num_simulations} Monte Carlo simulations of the FIFA 2026 World Cup...")
    
    # Track statistics
    stats = {
        name: {
            "group_stage_exit": 0,
            "r32": 0,
            "r16": 0,
            "qf": 0,
            "sf": 0,
            "finalist": 0,
            "winner": 0
        } for name in sim.teams.keys()
    }
    
    for i in range(num_simulations):
        results = sim.simulate_tournament(verbose=False)
        
        # Record stats
        stats[results["winner"].name]["winner"] += 1
        stats[results["winner"].name]["finalist"] += 1
        stats[results["runner_up"].name]["finalist"] += 1
        
        for team in [results["winner"], results["runner_up"]]:
            stats[team.name]["sf"] += 1
            stats[team.name]["qf"] += 1
            stats[team.name]["r16"] += 1
            stats[team.name]["r32"] += 1
            
        for team in results["sf_losers"]:
            stats[team.name]["sf"] += 1
            stats[team.name]["qf"] += 1
            stats[team.name]["r16"] += 1
            stats[team.name]["r32"] += 1
            
        for team in results["qf_losers"]:
            stats[team.name]["qf"] += 1
            stats[team.name]["r16"] += 1
            stats[team.name]["r32"] += 1
            
        for team in results["r16_losers"]:
            stats[team.name]["r16"] += 1
            stats[team.name]["r32"] += 1
            
        for team in results["r32_losers"]:
            stats[team.name]["r32"] += 1

    # Print results
    print("\n" + "="*85)
    print(f"{'TEAM':<20} | {'RATING':<8} | {'R32 %':<8} | {'R16 %':<8} | {'QF %':<8} | {'SF %':<8} | {'FINAL %':<8} | {'WIN %':<8}")
    print("="*85)
    
    sorted_teams = sorted(stats.items(), key=lambda x: x[1]["winner"], reverse=True)
    for name, team_stats in sorted_teams[:20]:  # Show top 20 teams
        rating = sim.teams[name].rating
        p_r32 = (team_stats["r32"] / num_simulations) * 100
        p_r16 = (team_stats["r16"] / num_simulations) * 100
        p_qf = (team_stats["qf"] / num_simulations) * 100
        p_sf = (team_stats["sf"] / num_simulations) * 100
        p_fin = (team_stats["finalist"] / num_simulations) * 100
        p_win = (team_stats["winner"] / num_simulations) * 100
        
        print(f"{name:<20} | {rating:<8} | {p_r32:>6.1f}% | {p_r16:>6.1f}% | {p_qf:>6.1f}% | {p_sf:>6.1f}% | {p_fin:>6.1f}% | {p_win:>6.1f}%")
    print("="*85)
    print("Note: The remaining 28 teams are not shown but are simulated in the background.")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    sim = WorldCupSimulation(TEAMS_DATA)
    
    # 1. Run a sample tournament simulation with full details
    print("=============================================================")
    print("      FIFA 2026 WORLD CUP SIMULATION - SAMPLE SINGLE RUN     ")
    print("=============================================================")
    sim.simulate_tournament(verbose=True)
    
    # 2. Run Monte Carlo simulation for prediction probabilities
    print("\n")
    run_monte_carlo(sim, num_simulations=5000)