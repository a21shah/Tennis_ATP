# Dictionary for points awarded in each tournament as of 2024 (250/500/Masters/GS/ATP Finals)
# https://en.wikipedia.org/wiki/ATP_rankings#Points_distribution_(2024%E2%80%93present)

# Points awarded for a 250 tournament with a 48 player draw (Top 16 seeds receive a bye to R32)
points_250_48 = {
    'W': 250,
    'F': 165,
    'SF': 100,
    'QF': 50,
    'R16': 25,
    'R32': 13,
    'R64': 0
}

# Points awarded for a 250 tournament with a 32 player draw
# Also applies to a 250 tournament with a 28 player draw (Top 4 seeds receive a bye to R16)
points_250_32 = {
    'W': 250,
    'F': 165,
    'SF': 100,
    'QF': 50,
    'R16': 25,
    'R32': 0,
}

# Points awarded for a 500 tournament with a 48 player draw (Top 16 seeds receive a bye to R32)
points_500_48 = {
    'W': 500,
    'F': 330,
    'SF': 200,
    'QF': 100,
    'R16': 50,
    'R32': 25,
    'R64': 0
}

# Points awarded for a 500 tournament with a 32 player draw
points_500_32 = {
    'W': 500,
    'F': 330,
    'SF': 200,
    'QF': 100,
    'R16': 50,
    'R32': 0
}

# Points awarded for a Masters 1000 tournaments with 96 player draw (Top 32 players recieve a bye to R64)
points_1000_96 = {
    'W': 1000, 
    'F': 650,
    'SF': 400,
    'QF': 200,
    'R16': 100,
    'R32': 50,
    'R64': 30,
    'R128': 10,
}

# Points awarded for a Masters 1000 tournaments with 96 player draw (Top 8 players recieve a bye to R32)
points_1000_56 = {
    'W': 1000, 
    'F': 650,
    'SF': 400,
    'QF': 200,
    'R16': 100,
    'R32': 50,
    'R64': 10
}

points_GS = {
    'W': 2000, 
    'F': 1300,
    'SF': 800,
    'QF': 400,
    'R16': 200,
    'R32': 100,
    'R64': 50,
    'R128': 10,
}

# ATP Finals: A player recieves points for every Round Robin match won (RR), and for winning the SF and F
# Player that wins all 3 RR matches, SF and F would get the max points available (1500)
points_ATP_Finals = {
    'F': 500,
    'SF': 400,
    'RR': 200, 
}