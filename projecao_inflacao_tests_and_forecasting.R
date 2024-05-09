library(readr)
library(forecast)
library(lmtest)
library(aTSA)
library(tstools)
library(urca)

tabela_IPCA <- read_csv2("./tabelas/IPCA/IPCA_long.csv")

ts_IPCA <- ts(tabela_IPCA$variacao[tabela_IPCA$id %in% c(0)],
           start = c(2006, 7),
           end = c(2024, 3),
           frequency = 12)

summary(tabela_IPCA$variacao[tabela_IPCA$id %in% c(0)])
ggtsdisplay(ts_IPCA)


# Testes de estacionariedade e homocedasticidade --------------------------


adf_IPCA0 <- ur.df(ts_IPCA,
                   type = "trend",
                   lags = 4,
                   selectlags = "AIC")

adf.test(ts_IPCA, nlag = 4, output = TRUE) #redundância

summary(adf_IPCA0)

#Pelo teste, temos que o lag1 (-2.861) está a direita dos valores críticos do teste
#logo, é possível rejeitar H_0 em favor da estacionariedade.

# Diagnóstico de modelo ARMA(p,q) -----------------------------------------

arma_aic <- auto.arima(ts_IPCA,
                       d=0,
                       max.p=4,
                       max.q=4,
                       ic = "aic",
                       seasonal = FALSE,
                       stepwise = FALSE,
                       approximation = FALSE,
                       trace = TRUE)

arma_bic <- auto.arima(ts_IPCA,
                       d=0,
                       max.p=4,
                       max.q=4,
                       ic = "bic",
                       seasonal = FALSE,
                       stepwise = FALSE,
                       approximation = FALSE,
                       trace = TRUE)

#seguindo o diagnóstico de ambos os modelos, o resultado é condizente com um ARMA(1,0)

ar1 <- arima(ts_IPCA, order = c(1,0,0))
summary(ar1)
coeftest(ar1)

checkresiduals(ar1)
#residuos destoam de uma normal

ts.diag(ar1)

k <- arimaorder(arma_aic)["p"] + arimaorder(arma_aic)["q"]
for (n in seq(4, 24, by = 4)) { # testa os lags sequencialmente de 4 em 4
  cat("Teste Ljung-Box com defasagem:", n,"\n")
  print(Box.test(residuals(ar1), lag = n, type = "Ljung-Box", fitdf=k))
}


# Retirando ouliers -------------------------------------------------------

outliers <- tsoutliers(ts_IPCA)
time(ts_IPCA)[outliers$index]

dummy_mar22 <- create_dummy_ts(end_basic = c(2024,3),
                                 dummy_start = c(2022,3),
                                 start_basic = c(2006, 7),
                                 frequency = 12,
                                 sp = TRUE)

regIPCA_dummy <- lm(ts_IPCA ~ dummy_mar22)
summary(regIPCA_dummy)

rIPCA_ex <- residuals(regIPCA_dummy)
ggtsdisplay(rIPCA_ex)

arma_aic_outliers <- auto.arima(ts_IPCA,
                                 xreg = dummy_mar22,
                                 d = 0,
                                 max.p = 4,
                                 max.q = 4,
                                 ic = "aic",
                                 seasonal = FALSE,
                                 stepwise = FALSE,
                                 approximation = FALSE,
                                 trace = TRUE)

arma_bic_outliers <- auto.arima(ts_IPCA,
                                 xreg = dummy_mar22,
                                 d = 0,
                                 max.p = 4,
                                 max.q = 4,
                                 ic = "bic",
                                 seasonal = FALSE,
                                 stepwise = FALSE,
                                 approximation = FALSE,
                                 trace = TRUE)


# Testes de significância sem outliers ------------------------------------

coeftest(arma_aic_outliers)

checkresiduals(arma_aic_outliers)

#Resultados de AIC e BIC são iguais


# Previsão ----------------------------------------------------------------

## subset time series (jul/2006 a dez/23)
ts_IPCAfcst <- window(ts_IPCA, start = c(2006, 7), end = c(2023, 12))

arma_aic_fcst <- auto.arima(ts_IPCAfcst,
                       d=0,
                       max.p=4,
                       max.q=4,
                       ic = "aic",
                       stepwise = FALSE,
                       approximation = FALSE,
                       trace = TRUE)

forecast_aic <- forecast::forecast(arma_aic_fcst, h = 3, level = c(50,68,90))
forecast_aic
plot(forecast_aic)
