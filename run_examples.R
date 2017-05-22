library(rstan)


rstan_options(auto_write = TRUE)

#model_name <- "basic_estimators/bernoulli"
#model_name <- "basic_estimators/normal_censored"
model_name <- "sensitivity_generator/normal_censored"

model <- stan_model(paste(model_name, "stan", sep="."))

stan_data <- new.env()
source(paste(model_name, "data.R", sep="."), local=stan_data)
stan_data$weights <- rep(1.0, stan_data$N_observed)

# Use chains=1 for now to avoid confusion around get_inits.
num_samples <- 500
result <- sampling(model, data=stan_data, chains=1, iter=num_samples * 2)
print(result)
result_draws <- extract(result, inc_warmup=FALSE)

model_sens <- stan_model(paste(model_name, "_sensitivity.stan", sep=""))
model_sens_fit <- stan(paste(model_name, "_sensitivity.stan", sep=""),
                       data=stan_data, algorithm="Fixed_param", iter=1, chains=1)

par_list <- get_inits(result, iter=100)[[1]]
par_list$weights <- stan_data$weights
par_list$y_var <- stan_data$y_var

# Sanity check that get_inites is doing what I think it is.
if (FALSE) {
  mu_inits <- unlist(sapply(1:num_samples,
                            function(n) { get_inits(result, iter=n + num_samples)[[1]]$mu[1] }))
  plot(sort(mu_inits), sort(result_draws$mu))
  abline(0, 1)
}

param_names <- result@.MISC$stan_fit_instance$unconstrained_param_names(FALSE, FALSE)
sens_param_names <- model_sens_fit@.MISC$stan_fit_instance$unconstrained_param_names(FALSE, FALSE)

grad_mat <- matrix(NA, num_samples, length(sens_param_names))
prog_bar <- txtProgressBar(min=1, max=num_samples, style=3)
for (n in 1:num_samples) {
  setTxtProgressBar(prog_bar, value=n)
  par_list <- get_inits(result, iter=n + num_samples)[[1]]
  for (par in ls(par_list)) {
    # get_inits is broken
    # https://github.com/stan-dev/rstan/issues/417
    par_list[[par]] <- as.numeric(par_list[[par]])
  }
  par_list$weights <- stan_data$weights
  par_list$y_var <- stan_data$y_var
  pars_free <- unconstrain_pars(model_sens_fit, par_list)
  grad_mat[n, ] <- grad_log_prob(model_sens_fit, pars_free)
}
close(prog_bar)

weight_rows <- grepl("weights", sens_param_names)

draws_mat <- extract(result, permute=FALSE)[,1,]
sens_mat <- cov(grad_mat, draws_mat)
plot(stan_data$y, sens_mat[weight_rows, 1])
