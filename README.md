# ATP Points to Defend

Calculate how many points each player is defending per tournament by analyzing their results on the ATP Tour(Singles) in 2025.


### First Iteration: For the first iteration of the project, the dataset from Kaggle was used.
Kaggle: [ATP Tennis 2000 - 2026 Daily update](https://www.kaggle.com/datasets/dissfya/atp-tennis-2000-2023daily-pull/data?select=atp_tennis.csv)

However, that data did not contain any walkovers or withdraws. Brisbane 2025 for instance had a case where there was a walkover in the Final and in the SF. Without knowing who won the tournament, there was insufficient data to backfill missing data. Thus this data was dropped in preference for another dataset.


### Second Iteration: Dataset from Jeff Sackmann
Data: [ATP Matches](https://github.com/JeffSackmann/tennis_atp)
Currently the 2025 match file is not available, so we'll use the 2024 for now.
Note: The dataset only contains the main round matches played on the ATP Tour and does not contain matches played in Qualifiers.