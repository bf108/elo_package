## Understanding ELO

The fundamentals of ELO predictions assume that each players skill can be represented as continuous probability distribution, commonly known as normal or [Gaussian distritbution](https://en.wikipedia.org/wiki/Normal_distribution).
Each player will then have a mean "skill' and 'variance' - squared deviation from the mean.

##### Probability Density Function (PDF) and Cumulative Distribution Function (CDF)
Original implementations of ELO assumed that each player's skill was a normally distributed real-valued random variable. To determine the probability that one player would beat another, you had to evalute the probability that

<img src="https://render.githubusercontent.com/render/math?math=$X_1$  ~ $N(\mu_1,\sigma_1^2)$"> would return a higher skill than: <img src="https://render.githubusercontent.com/render/math?math=$X_2$ ~ $N(\mu_2,\sigma_2^2)$">

![alt text](https://github.com/bf108/elo_package/blob/master/static/compare_player_skill.png?raw=true)

#### So how do we determine likelihood of Player A beating Player B?
All randomly distributed variables can be represented as a linear combination of other randomly distributed variables. Therefore, the problem outlined above can be summarised as follows:

<img src="https://render.githubusercontent.com/render/math?math=P(X_1 > X_2) = P(X_1 - X_2 > 0) = 1 - P(X_1 - X_2 < 0)">

Linear Combination of Means:

<img src="https://render.githubusercontent.com/render/math?math=\mu = E(X_1 - X_2) = \mu_1 - \mu_2">

Standard Deviation

<img src="https://render.githubusercontent.com/render/math?math=\sigma = Var(X_1 - X_2) = \sqrt{\sigma_1^2  +  \sigma_2^2}">

Determining the probability that this new linear combination is greater than zero can be achieved by comparing this distribution to the Standard Normal Distribution <img src="https://render.githubusercontent.com/render/math?math=$Z$ ~ $N(0,1)$">:

<img src="https://render.githubusercontent.com/render/math?math=X = Z\sigma + \mu">

Therefore:

<img src="https://render.githubusercontent.com/render/math?math=P(X_1 - X_2 > 0) = P(X > 0) = P(Z\sigma + \mu > 0) = P(Z > \frac{-\mu}{\sigma}) = \phi{(\frac{-\mu}{\sigma})}u">

This problem has been reduced to calculating whether the cumulative distribution function (CDF) <img src="https://render.githubusercontent.com/render/math?math=\phi"> is greater than some mean divided by some standard deviation.

![alt text](https://github.com/bf108/elo_package/blob/master/static/expected_probability.png?raw=true)

#### Logistic Function
New versions of ELO use the logistic function instead of the CDF:

<img src="https://render.githubusercontent.com/render/math?math=f(x) = \frac{L}{1-e^{-k(x-x_0)}}">

- $L$ maximum value of function $\lim_{x \to +\infty}$
- $k$ steepness factor of logistic function
- $x_o$ - Value of $x$ at mid point

The normal logistic function can be transformed to provide the probability that one player will beat another as show below:

<img src="https://render.githubusercontent.com/render/math?math=p_A=\frac{1}{1 + b^-\frac{d}{s}}">

- $p_A$ : probability of player A winning
- $b$ : base (this can be 10, $e$ etc)
- $d$ : difference between player mean skill
- $s$ : scale factor (Constant Standard Deviation of player rating $\sigma$=200)


If we use base 10, instead of natural logarithm used in original logistic function we get the below formula:

<img src="https://render.githubusercontent.com/render/math?math=E_A=\frac{1}{1+10^\frac{R_B-R_A}{s}}">

- $E_A$ - Expected probability of Player $A$ winning.
- $R_B$ - Player $R_B$ mean rating*
- $R_A$ - Player $R_A$ mean rating*
- $s$ : scale factor (Constant Standard Deviation of player rating $\sigma$=200)

*Mean rating of a player assumed normally (Gaussian) distributed skill.

![alt text](https://github.com/bf108/elo_package/blob/master/static/logistic_vs_cdf.png?raw=true)


#### Then how does a Players Rating Change after a match?

With basic ELO we ues the following equation:

<img src="https://render.githubusercontent.com/render/math?math=\delta = (actual - expected) * K_{factor}">
<img src="https://render.githubusercontent.com/render/math?math=\delta = score_{new} = score_{prior} + \delta">

This takes the predicted outcome of match. i.e Probabiliy of player A beating player B and compares it to the actual outcome. 

- When the outcome is close to the expected, the result of this expression tends to 0
- However when the prediction is very different from the outcome this value can tend to either -1 or 1.

The above value is multiplied by some factor to determine the change to a player rating. So when the prediction is **very** right, then player rating change is small. However, when the prediction is **very** wrong, the player rating change is large.

This k-factor is basically the speed at which the algorithm converages on the true rating of a player. Too low a k-factor and it will take too many game for players ratings to converage and users will lose interest, but too high and the rating will be too volatile and attribute too much importance to single games.


![alt text](https://github.com/bf108/elo_package/blob/master/static/player_rating_history.png?raw=true)

## Pros & Cons of ELO

The basic ELO methodology doesn't account for the following:

- Multi-player settings
- Agnostic to significance of actual match - Basic club match vs national champs final
- Home Advantage
- Margin of Victory
- No consideration to degregation of player ratings over time if not playing.
 - This can discourage top ranked players from playing.
- Players skill distribution remains fixed. Potentially unrealistic for experienced players who could be said to have a narrower range of typical performance.


#### Benefits of remaining with a Basic ELO System

- Simple ELO systems have been proven to be effective in many sports.
- Trying to account for the above additional factors will always incur some subjectivity when selecting parameters.
- The impact on ratings becomes less clearly defined and can result in lower player satisfication if they can't easily see the link between performance and overall rating.
- The more complex approach are also prone to cheating, if players are able to identify scenarios in which to boost their scores unfairly due to some limitations/edge cases in the logic.


## Extending Basic ELO

### Assumptions

- Matches where points aren't recorded are dorpped/not counted.
- All unrated players begin with a skill of 1500
- If a player doesn't have a tsid, then they are assumed to be a new player and given a generated tsid begining with 2,000,0001
    - This will repeatedly be the case if they appear in a tournament more than once because with name alone it is impossible to distinguish between players.

### Margin of Victory

Methodology:

* 1 - Dropped matches where score wasn't present - e.g n/a
* 2 - Converted scores saved as list to strings
* 3 - Found overall pts difference to winner over match
* 4 - Found pts difference for individual games within a match


Summary of Points Difference Analysis
- **The mean pts_diff observed was 11.7 points**
- The max pts_diff observed is unsurprisingly 42, which accounts for 21-0 each game.
- We do also see a small number of occassions where the pts_diff was actually negative for the winner, indicating that there were some games which they lost by a significant margin despite winning overall.

The points difference change attributed to MOV follows the below function:

![alt text](https://github.com/bf108/elo_package/blob/master/static/MOV_factor.png?raw=true)


[Auto-correlation](https://en.wikipedia.org/wiki/Autocorrelation) is the correlation of a signal with the delayed copy of itself. With our example, we are assuming that the probability of Player A winning his next match is correlated to his performance in his previous match. In the case where a player wins many matches, each time increasing their rating, this may result in a an artificially inflated rating which results in a large correction when eventually losing a match. To prevent auto-correlation we discount the scaling factor applied to the points of winner and reduce it for the losers. This makes the algorithm less sensitive to recent matches.

![alt text](https://github.com/bf108/elo_package/blob/master/static/ACF.png?raw=true)


### Extending to Doubles Matches

The idea behind extending ELO to doubles matches centers on the principle that all random normal distributions can be formed from a linear combination of other normal random distributions.

Therefore if we consider two individual players each with mean skill and variance $\mu_1$ and $\mu_2$ $\sigma_{1}^2$ and $\sigma_{2}^2$ respectively, we can in theory take the combination of the two as new player.

This then allows us to estimate the likelihood of one pair of players beating another pair of players.

When it comes to re-rating the players after the result, some consideration should be given to ensure this is correctly attributed. This is a subjective matter but I offer the following approach.

- Two equally skilled players (P1 == P2) should half the distribution of the points.
- When skill of P1 > P2, then P1 should recieve less of the points change.
- When skill of P1 < P2, then P1 should recieve more of the points change.

Subjective justification for this argument:

- Stronger player on team can only control play when they serve or receive serve which is at most 50% of points. However, the opposition will, where possible, play shots to the weakest member of the oppoosition. Thereby likely reducing the percentage of occassions that the stronger player can control the match. This percentage skew will increase more when the difference in skill between doubles parterns is higher and opposition can easily identify weaker player.

A reasonable points split can then be achieved with an application of the logistic function, comparing the difference in doubles players mean skill, to the constant standard deviation applied to all players.

## Evaluating the Algorithm

#### Basic Accuracy
Count on how many occassions the prediction made by model was correct.

#### Brier Score
This will compare the prediction compared to the reality. Large expected results which are correct are rewarded highly, but incorrect ones are greatly punished also because it is comparing a square of the distance.

Wiki Reference [Brier Score](https://en.wikipedia.org/wiki/Brier_score) 

<img src="https://render.githubusercontent.com/render/math?math=BS = \frac{1}{N}\sum_{t=1}^{N}(f_t - o_t)^2">

$BS$ - Brier Score

$N$ - Number of forecasting instances

$f_t$ - Forecast probability for particular observation

$o_t$ - Actual outcome of the event



## Using this Package

Player Class

src/elopackage/player.py

This class is used to create Player Objects which have attributes:

- Name
- TSID (unique identifier)
- Rating
- Standard Deviation of Rating
- k-factor - Factor by which to update ratings

It also has a range of method for:

- updating player rating
- visualize competitors skill vs their own
- visualize probability of winning against competitor
- visualize how their rating has changed overtime


Elo Class

src/elopackage/elo.py

This class is used to provide:

- probability of Player A beating Player B
- rating change to a player/team after a certain victory.
  - Here you can use a basic approach which just considers Win/Loss as binary event
  - or you can be more complex and include Margin of Victor and Auto-Correlation Factors


ResultTable Class

src/elopackage/results.py

This class applies the Player and Elo classes to collected data and was used to optimize parameters to improve predictive ability of the algorithm.


