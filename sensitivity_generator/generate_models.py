import os

data_block = """
real U;
int<lower=0> N_censored;
int<lower=0> N_observed;
real<upper=U> y[N_observed];
"""

# TODO: strip constraints out of the hyperparameters.
hyperparameters_block = """
real weights[N_observed];
real<lower=0> y_var;
"""

parameters_block = """
real mu;
"""


model_block = """
for (n in 1:N_observed) {
  target += weights[n] * (
    normal_lpdf(y[n] | mu, y_var) - normal_lcdf(U | mu, y_var));
}
target += N_censored * log1m(normal_cdf(U, mu, y_var));
"""

extra_blocks = """
"""

out_dir = '/home/rgiordan/Documents/git_repos/example-models/sensitivity_generator'
model_name = 'normal_censored'

f = open(os.path.join(out_dir, model_name + '.stan'), 'w')

f.write('data {\n')
f.write(data_block)
f.write(hyperparameters_block)
f.write('}\n')

f.write('parameters {\n')
f.write(parameters_block)
f.write('}\n')

f.write('model {\n')
f.write(model_block)
f.write('}\n')

f.write(extra_blocks)

f.close()


f = open(os.path.join(out_dir, model_name + '_sensitivity.stan'), 'w')

f.write('data {\n')
f.write(data_block)
f.write('}\n')

f.write('parameters {\n')
f.write(parameters_block)
f.write(hyperparameters_block)
f.write('}\n')

f.write('model {\n')
f.write(model_block)
f.write('}\n')

f.write(extra_blocks)

f.close()
