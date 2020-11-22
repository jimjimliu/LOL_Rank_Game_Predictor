<p align="center">
<img src="https://github.com/jimjimliu/LOL_Match_Prediction/blob/master/img/waterloo_engineering_logo_horiz_rgb.png" alt="fnc" width="70%"/>
</p>
<p align="center">
<img src="https://github.com/jimjimliu/LOL_Match_Prediction/blob/master/img/lol.png" alt="fnc" width="70%"/>
</p>


<h1 align = "center">League of Legends Rank Match Predictor</h1>
<p align="center">
predict ranked solo-queue matches
</p>



### Introduction

The system is a fully functioning AI agent to make a prediction of any active ranked solo queue match. Please note that the predictor is only able to predict an active ranked game that is running on your local machine. You can only use it to predict your own game. RIOT does not provide any APIs to retrieve others' active ranked games.

### Abstract

> To build such a system, we've collected 235,487 player accounts  of all rank divisions. 7,220  accounts  were  randomly  selected.  Roughly  250 accounts were selected for each rank(i.e.  DiamondII) so that the data are evenly distributed along 24 ranks. 20 most recent ranked games are collected from each player’s account. The final data set contains 119,184 game instances. All the data were extracted from the APIs provided by RIOT company at https://developer.riotgames.com/apis. 
>
> By using neural network and logistic regression, we reached a testing accuracy over 96%.  

### To Run

> There are two things you need to configure before you are able to run the system. 
>
> 1, Go to https://developer.riotgames.com, use your game account id and pswd to login.
>
> Generate a DEVELOPMENT API KEY once you are logged in.
>
> Copy that API Key, go to directory `Config/riot_config.py` and put your key there. For example:
>
> ```python
> ACCESS_KEY = "RGAPI-2cc1fe35-adsa7-4a84-95b6-7dfdfd1d02e91"
> ```
>
> The key serves as an access for you to retrieve any history game data and your active game data. 

> 2, Next, go to `Live_Game_Prediction.py`, configure your own player name.
>
> ```python
> if __name__ == '__main__':
>     player_name = "your player name"
>     GamePredict(player_name).predict()
> ```

> Finally, once you've started a RANKED game on your local machine, run
>
> ```python
> python3 Live_Game_Prediction.py
> ```
>
> The system makes prediction every 60 seconds.

### Sample Output

```python
users@MacBook-Pro LOL_Match_Prediction % python3 Live_Game_Prediction.py
Blue team win rate: 48.94%
Red team win rate: 51.06%

Blue team win rate: 55.97%
Red team win rate: 44.03%

Blue team win rate: 66.96%
Red team win rate: 33.040000000000006%

Blue team win rate: 61.260000000000005%
Red team win rate: 38.74%
.
.
.
.
.
Blue team win rate: 16.09%
Red team win rate: 83.91%

Blue team win rate: 19.63%
Red team win rate: 80.36999999999999%

Blue team win rate: 24.279999999999998%
Red team win rate: 75.72%
```

### Files

TODO

### Testing

TODO



























