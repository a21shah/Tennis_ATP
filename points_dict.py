# Dictionary for points awarded in each tournament (250/500/ATP Masters/GS/ATP Finals)
# https://en.wikipedia.org/wiki/ATP_rankings#Points_distribution_(2024%E2%80%93present)

points_250 = {
    'W': 250,
    'F': 165,
    'SF': 100,
    'QF': 50,
    'R16': 25,
    'R32': 13,
}

points_500 = {
    'W': 500,
    'F': 330,
    'SF': 200,
    'QF': 100,
    'R16': 50,
    'R32': 25,
}

# There are two different types of ATP Masters. 
# 7 ATP Masters 1000 events have a 96 player draw. The top 32 players recieve a bye into the 2nd round.
# Monte-Carlo and Paris have a 56 player draw and thus have one less round. The top 8 players recieve a bye into the 2nd round.
points_1000 = {
    'W': 1000, 
    'F': 650,
    'SF': 400,
    'QF': 200,
    'R16': 100,
    'R32': 50,
    'R64': 30,
    'R128': 10,
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

# ATP Finals a player recieves points for every Round Robin match won (RR)
points_ATP_Finals = {
    'W': 900,
    'F': 400,
    'RR': 200, 
}