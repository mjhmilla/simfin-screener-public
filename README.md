# screener
@author Matthew Millard
@date November 2021


# Quick Start

1. Open 'mainScreener.py' and set 'YOUR_LOCAL_DIRECTORY_HERE' to the local directory this file resides in. This is where the database files from SimFin will be downloaded.

2. Set the API key and SimFin directory
  a. Register with simfin to get a free api-key and replace YOUR_FREE_SIMFIN_API_KEY_HERE with your api key.
  b. If you have a paid account for Sim-Fin+, replace YOUR_SIMFIN_API_PLUS_KEY_HERE with your api key and set flag_SimFinApiPlusKey to true.

3. Run the screener: run 'python3 mainScreener.py' from the command line

What does the SimFin+ api key give you? Access to the derived data base, which in turns gives you access to the following information used by the business ranking and valuation: equity-per-share, earnings-per-share, sales-per-share, and free-cash-flow-per-share.

# Overview

This is a screener that algorithmically implements the screening algorithm described in Phil Town's book 'Rule #1 Investing' with some minor modifications. First, companies are analyzed for growth and a conservative value of their stock is calculated. Next, the companies are returned that rank highest on a combination of both growth and margin of safety (value/price) are placed in the 'overall' category; an alternate ranking by growth is output to the 'growth' category; an alternate ranking by margin-of-safety is output to the 'marginOfSafety' category; and finally the overall ranking for small companies (< 1billion market cap) are in the 'small' category. Finally, the output is placed in tabular form in the output folder with plots on the top 15 companies placed in the folder for each country analyzed. At the moment the plotting functionality is time consuming (matplotlib is slow).

# 1. Growth Metrics

1. Return on Enterprise average. 

Town recommends using return on equity. However, according Greenblatt it is much harder to manipulate the return on enterprise with creative accounting than the return on equity. In addition, most people pay close attention to the return on equity, and so many firms have an incentive to manipulate this figure to some degree. Here instead I choose to use the Return on Enterprise instead. For more information:


Equity: totalAssets - totalLiabilities
      : the amount of money that is left if all of the assets are sold and the debt is paid off
      : https://www.investopedia.com/terms/e/equity.asp

Enterprise value: marketCapitalization + totalDebt - cash
      : The take over value of the company
      : https://www.investopedia.com/terms/e/enterprisevalue.asp


Greenblatt J. The little book that still beats the market. John Wiley & Sons; 2010 Aug 26.

2. Equity per share growth
3. Earnings per share growth
4. Sales per share growth
5. Free cash flow growth

To evaluate growth I solve for an exponential curve of best fit to the data:

  y(x) = A(1+p)^x + B

where y is the value of some metric over time, x is the years over which we have data (unbiased so that x(0)=0), p is the interest rate, A is a scale factor, and B is an offset. Here we choose 

  B = -min(0, min(y))

so that y+B always has values greater than zero. Taking logarithms allows us to turn this into a linear relationship

log (y-B) = log(A) + x(log(1+p))

We can solve for A and p to minimize the sum of squared errors using

[x, 1](log(1+p))  = log(y-B)
      (log(A))  

where

(log(1+p))  = inv([x,1]^t [x, 1]) ([x,1]^t log(y-B))
(log(A))  

# 2. Growth Ranking

Each metric is ranked from biggest to smallest and given a numeric rank from 1 to N. The over all best company is defined as the company that minmizes the sum of all of the rankings

# 3. Margin of Safety

Town recommends evaluating the value per share N years in the future using

  valePerShare_N = min(PE_0, equity_growth x 2 x 100) earningPerShare_0 (1+equity_growth)^N

and then bringing that future value back to the present using the desired minimum rate of return

  valuePerShare_0 = valuePerShare_N / (1+minRateOfReturn)^N

Finally, the margin of safety is defined as

  marginOfSafety = valuePerShare_0 / price

Town recommends looking for great businesses that have a margin of safety of 0.5 or less.

# 4. Margin of Safety Ranking

Every company is ranked from the best margin of safety (the lowest numerical number) to the worst margin of safety.

# Overall Ranking

Is the company that has the lowest some of the growth ranking and the margin of safety ranking












