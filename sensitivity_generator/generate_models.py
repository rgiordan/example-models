import argparse
import os

# data_block = """
#     real U;
#     int<lower=0> N_censored;
#     int<lower=0> N_observed;
#     real<upper=U> y[N_observed];
# """
#
# # TODO: strip constraints out of the hyperparameters.
# hyperparameters_block = """
#     real weights[N_observed];
#     real y_var;
# """
#
# parameters_block = """
#     real mu;
# """
#
#
# model_block = """
# for (n in 1:N_observed) {
#   target += weights[n] * (
#     normal_lpdf(y[n] | mu, y_var) - normal_lcdf(U | mu, y_var));
# }
# target += N_censored * log1m(normal_cdf(U, mu, y_var));
# """
#
# extra_blocks = """
# """


parser = argparse.ArgumentParser(
    description='Generate stan models for sensitivity analysis.')
parser.add_argument('--model_name', help='Directory and base filename for stan scripts.')
args = parser.parse_args()

f = open(args.model_name + '_data_block.stanblock', 'r')
data_block = f.read()
f.close()

f = open(args.model_name + '_model_block.stanblock', 'r')
model_block = f.read()
f.close()

f = open(args.model_name + '_parameters_block.stanblock', 'r')
parameters_block = f.read()
f.close()

f = open(args.model_name + '_hyperparameters_block.stanblock', 'r')
hyperparameters_block = f.read()
f.close()

extra_blocks_fname = args.model_name + '_extra_blocks.stanblock'
if os.path.isfile(extra_blocks_fname):
    f = open(extra_blocks_fname, 'r')
    extra_blocks = f.read()
    f.close()
else:
    extra_blocks = ''


f = open(os.path.join(args.model_name + '.stan'), 'w')

f.write('data {\n')
f.write(data_block)
f.write(hyperparameters_block)
f.write('\n}\n')

f.write('parameters {\n')
f.write(parameters_block)
f.write('\n}\n')

f.write('model {\n')
f.write(model_block)
f.write('\n}\n')

f.write(extra_blocks)
f.write('\n')

f.close()


f = open(os.path.join(args.model_name + '_sensitivity.stan'), 'w')

f.write('data {\n')
f.write(data_block)
f.write('\n}\n')

f.write('parameters {\n')
f.write(parameters_block)
f.write(hyperparameters_block)
f.write('\n}\n')

f.write('model {\n')
f.write(model_block)
f.write('\n}\n')

f.write(extra_blocks)
f.write('\n')

f.close()
