from manim import *
import numpy as np
from scipy.special import logsumexp


class MonteCarloIntro(Scene):
    def construct(self):
        return super().construct()

class HMCDiffuculty(Scene):
    def construct(self):
        return super().construct()

class FlowMCIdea(Scene):
    def construct(self):
        return super().construct()

class Autodiff(Scene):
    def construct(self):
        return super().construct()

class Vmap(Scene):
    def construct(self):
        return super().construct()

####################
# Show target TargetDistribution
####################

def dualmoon(x):
    """
    Term 2 and 3 separate the distribution and smear it along the first and second dimension
    """
    term1 = 0.5 * ((np.linalg.norm(x) - 2) / 0.1) ** 2
    term2 = -0.5 * ((x[:1] - np.array([-4.0,5.0])) / 0.8) ** 2
    return -(term1 - logsumexp(term2))

# dualmoon = jax.jit(dualmoon)

class TargetDistribution(Scene):

    def add_graph(self, level):
        graph = ImplicitFunction(
            lambda x, y: dualmoon(np.array([x, y]))+level,
            color=BLUE,
            y_range=[-3,3],
            x_range=[-3,3],
        )
        return graph

    def construct(self):
        graphs = []
        level_set = [15, 10, 5, 0]
        for i in range(len(level_set)):
            graphs.append(self.add_graph(level_set[i]))
            graphs[-1].set_opacity(0.2+0.2*i)
            graphs[-1].set_stroke(width=0.)
        self.play(AnimationGroup(*[FadeIn(graph) for graph in graphs], lag_ratio=0.5))

        walker = Dot(np.array([1.0,1.0,0]))
        self.play(FadeIn(walker))
        self.play(walker.animate().move_to(np.array([1.3,1.0,0])))