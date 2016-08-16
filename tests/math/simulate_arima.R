library("forecast")
x <- WWWusage

arima.object <- Arima(x, order=c(2,0,0))
arima.object

starting.values <- 0
model <- list(arma=c(2,0,0,0,0,0,0), coef=list(ar1=0.86, ar2=-0.04, intercept=-0.13), sigma2=0.3)
new.arima.object <- Arima(starting.values, model=model)
new.arima.object$sigma2 = 0.3

plot(x, xlim=c(1, 200))
s<-simulate.Arima(new.arima.object, 200)
lines(s, col="red")
plot(s)
