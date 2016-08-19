# function from http://arxiv.org/pdf/1212.2393.pdf

# Simulating the Continuation of a Time Series in R
# December 12, 2012
# Halis Sak, Wolfgang Hörmann

# with bugs fixed

arima.condsim <- function(object, data, n.ahead = 1, n = 1){
    L <- length(data); coef <- object$coef;
    arma <- object$arma; model <- object$model;
    p <- length(model$phi); q <- length(model$theta)
    d <- arma[6]; s.period <- arma[5];
    s.diff <- arma[7]
    if(s.diff > 0 && d > 0){
        diff.xi <- 0;
        dx <- diff(data, lag = s.period, differences=s.diff)
        diff.xi[1] <- dx[length(dx) - d + 1];
        dx <- diff(dx, differences = d)
        diff.xi <- c(diff.xi[1], data[(L - s.diff * s.period + 1):L])
    }else if(s.diff > 0){
        dx <- diff(data, lag = s.period, differences = s.diff)
        diff.xi <- data[(L - s.diff * s.period + 1):L]
    }else if(d > 0){
        dx <- diff(data, differences = d);
        diff.xi <- data[(L - d + 1):L]
    }else{dx <- data}
    use.constant <- is.element("intercept", names(coef))
    mu <- 0
    if(use.constant){
        mu <- coef[sum(arma[1:4]) + 1][[1]] * (1 - sum(model$phi))
    }
    p.startIndex <- length(dx) - p
    start.innov <- NULL
    if(q > 0){
        start.innov <- residuals(object)[(L - q + 1):(L)]
    }
    res <- array(0, c(n.ahead, n))
    for(r in 1:n){
        innov = rnorm(n.ahead, sd = sqrt(object$sigma2))
        if(q > 0){
            e <- c(start.innov, innov)
        }else{e <- innov}
        xc <- array(0, dim = p + n.ahead)
        if(p != 0) for(i in 1:p) xc[i] <- dx[[p.startIndex + i]]
        k <- 1
        for(i in (p + 1):(p + n.ahead)){
            xc[i] <- e[q + k]
            if(q != 0)
            xc[i] <- xc[i] + sum(model$theta * e[(q + k - 1):k])
            if(p != 0)
            xc[i] <- xc[i] + sum(model$phi * xc[(i - 1):(i - p)])
            if(use.constant)
            xc[i] <- xc[i] + mu
            k <- k + 1
        }
        xc <- as.vector(unlist(xc[(p + 1):(p + n.ahead)]))
        if((d > 0) && (s.diff > 0)){
            xc <- diffinv(xc, differences = d, xi = diff.xi[1])[-c(1:d)]
            xc <- diffinv(xc, lag = s.period, differences = s.diff,
            xi = diff.xi[2:(s.diff * s.period + 1)])
            xc <- xc[-(1:(s.diff * s.period))]
        }else if(s.diff > 0) {
            xc <- diffinv(xc, lag = s.period, differences = s.diff,
            xi = diff.xi[1:(s.diff * s.period)])
            xc <- xc[-(1:(s.diff * s.period))]
        }else if(d > 0){
            xc <- diffinv(xc, differences = d, xi = diff.xi)[-c(1:d)]
        }
        res[, r] <- xc
    }
    res
}
