# ETF-SPZY

For this project, I decided to develop my own ttrading strategy/ETF. This startegy consists of a portfolio that owns the underlting stock of SPX and buys out-of-the-money puts and sells out-of-the-money calls as a hedging mechanism against sharp downturns. Consequently, it also minimizes gains during sharp upturns. We buy an equal amount of puts and sell an equal amount of calls. If the underlying falls below the put price, we are able to sell all of our underlying at that put strike price, effectively limiting our losses to the put price. Similarly, we must sell our underlying for the call strike price if it is to rise above the call strike. The way we choose our options is by first verifying that the option in question is liquid enough. We do this by measuring the volume of the option and the bid-ask spread. Next, we use a value, rho, to determine how far out-of-the-moeny to look. Furthermore, we only handle these options on every Friday. The options expire on the next Friday (one week in length). Through this strategy, we are able to enjoy the relatively steady growth of SPX while also guarding aginst large downturns.
