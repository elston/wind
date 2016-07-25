data = read.csv("../data/esios/esios.csv")

lambdaD.model <- arima(log(data["lambdaD"]), order = c(2, 0, 1),
               seasonal = list(order = c(1, 1, 1), period = 24))
lambdaD.model

MAvsMD.model <- arima(data["MAvsMD"], order = c(1, 0, 11),
                       seasonal = list(order = c(1, 0, 1), period = 24))
MAvsMD.model

imbalance.model <- arima(data["imbalance"], order = c(2, 0, 1),
                      seasonal = list(order = c(1, 0, 1), period = 24))
imbalance.model
