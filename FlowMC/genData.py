from flowMC.sampler.Gaussian_random_walk import GaussianRandomWalk
from flowMC.utils.PRNG_keys import initialize_rng_keys
import jax
import jax.numpy as jnp
from jax.scipy.special import logsumexp
from flowMC.sampler.Sampler import Sampler
from flowMC.nfmodel.rqSpline import RQSpline
import numpy as np

def dualmoon(x):
    """
    Term 2 and 3 separate the distribution and smear it along the first and second dimension
    """
    term1 = 0.5 * ((jnp.linalg.norm(x) - 2) / 0.1) ** 2
    term2 = -0.5 * ((x[:1] - jnp.array([-4.0,5.0])) / 0.8) ** 2
    return -(term1 - logsumexp(term2))

n_dim = 2
n_chains = 50
n_local_steps = 40
n_global_steps = 20
step_size = 0.1
n_loop_training = 10
n_loop_production = 10
num_epochs = 30
learning_rate = 1e-2

rng_key_set = initialize_rng_keys(n_chains, seed=42)

initial_position = jax.random.normal(rng_key_set[0], shape=(n_chains, n_dim)) * 1

RWMCMC = GaussianRandomWalk(dualmoon, True, {"step_size": step_size})

local_sampler_caller = lambda x: RWMCMC.make_sampler()
model = RQSpline(n_dim, 10, [128, 128], 8)

print("Initializing sampler class")

nf_sampler = Sampler(
    n_dim,
    rng_key_set,
    local_sampler_caller,
    {'dt':1e-2},
    dualmoon,
    model   ,
    n_loop_training=n_loop_training,
    n_loop_production=n_loop_production,
    n_local_steps=n_local_steps,
    n_global_steps=n_global_steps,
    n_chains=n_chains,
    n_epochs=num_epochs,
    learning_rate=learning_rate,
    use_global=False,
)

nf_sampler.sample(initial_position)

prod = nf_sampler.get_sampler_state(training=False)
chains = prod['chains']
local_accs = prod['local_accs']
np.savez('./dualmoon_data_local', chains = chains, local_accs = local_accs)

n_local_steps = 20
n_global_steps = 20

nf_sampler = Sampler(
    n_dim,
    rng_key_set,
    local_sampler_caller,
    {'dt':1e-2},
    dualmoon,
    model   ,
    n_loop_training=n_loop_training,
    n_loop_production=n_loop_production,
    n_local_steps=n_local_steps,
    n_global_steps=n_global_steps,
    n_chains=n_chains,
    n_epochs=num_epochs,
    learning_rate=learning_rate,
    use_global=True,
    max_samples=30000,
)

nf_sampler.sample(initial_position)

prod = nf_sampler.get_sampler_state(training=False)
chains = prod['chains']
local_accs = prod['local_accs']
global_accs = prod['global_accs']
nf_samples = nf_sampler.sample_flow(n_samples=10000)
prod_train = nf_sampler.get_sampler_state(training=True)
train_chains = prod_train['chains']

np.savez('./dualmoon_data_global', chains = chains, local_accs = local_accs, nf_samples = nf_samples, global_accs = global_accs,train_chains = train_chains)



from flowMC.nfmodel.rqSpline import RQSpline
import jax
import jax.numpy as jnp  # JAX NumPy

from flowMC.nfmodel.utils import *
from flax.training import train_state  # Useful dataclass to keep train state
import optax  # Optimizers
import flax

num_epochs = 100
batch_size = 10000
learning_rate = 0.001
momentum = 0.9
n_layers = 10
n_hidden = 100
dt = 1 / n_layers


key1, rng, init_rng = jax.random.split(jax.random.PRNGKey(0), 3)
model = RQSpline(2, 8, [64, 64], 8)

def create_train_state(rng, learning_rate, momentum):
    params = model.init(rng, jnp.ones((1, 2)))["params"]
    tx = optax.adam(learning_rate, momentum)
    return train_state.TrainState.create(apply_fn=model.apply, params=params, tx=tx)

state = create_train_state(init_rng, learning_rate, momentum)
train_flow, train_epoch, train_step = make_training_loop(model)

def sample_flow(data, rng, state):
    variables = model.init(rng, jnp.ones((1, 2)))["variables"]
    variables = variables.unfreeze()
    variables["base_mean"] = jnp.mean(data, axis=0)
    variables["base_cov"] = jnp.cov(data.T)
    variables = flax.core.freeze(variables)

    rng, state, loss_values = train_flow(
        rng, state, variables, data, num_epochs, batch_size
    )

    nf_samples = sample_nf(
        model,
        state.params,
        rng,
        1000,
        variables,
    )

    return rng, state, nf_samples

nf_samples_array = []
for i in range(20):
    rng, state, nf_samples = sample_flow(train_chains[:,:i*40].reshape(-1,2), rng, state)
    nf_samples_array.append(nf_samples[1])

np.savez('./dualmoon_nf_samples', nf_samples_array = nf_samples_array)

