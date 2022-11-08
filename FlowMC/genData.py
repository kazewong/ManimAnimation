from flowMC.sampler.Gaussian_random_walk import GaussianRandomWalk
from flowMC.utils.PRNG_keys import initialize_rng_keys
import jax
import jax.numpy as jnp
from jax.scipy.special import logsumexp
from flowMC.sampler.Sampler import Sampler
from flowMC.nfmodel.rqSpline import RQSpline

def dualmoon(x):
    """
    Term 2 and 3 separate the distribution and smear it along the first and second dimension
    """
    term1 = 0.5 * ((jnp.linalg.norm(x) - 2) / 0.1) ** 2
    term2 = -0.5 * ((x[:1] - jnp.array([-4.0,5.0])) / 0.8) ** 2
    return -(term1 - logsumexp(term2))

n_dim = 2
n_chains = 15
n_local_steps = 30
n_global_steps = 30
step_size = 0.03
n_loop_training = 3
n_loop_production = 5
num_epochs = 30
learning_rate = 1e-2

rng_key_set = initialize_rng_keys(n_chains, seed=42)

initial_position = jax.random.normal(rng_key_set[0], shape=(n_chains, n_dim)) * 1

RWMCMC = GaussianRandomWalk(dualmoon, True, {"step_size": step_size})

local_sampler_caller = lambda x: RWMCMC.make_sampler()
model = RQSpline(n_dim, 4, [32, 32], 8)

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
    use_global=True,
)

nf_sampler.sample(initial_position)

prod = nf_sampler.get_sampler_state(training=False)
chains = prod['chains']
local