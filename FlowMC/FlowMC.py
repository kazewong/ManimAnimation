from manim import *
import numpy as np
from scipy.special import logsumexp
from scipy.stats import gaussian_kde

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

data_global = np.load('./dualmoon_data_global.npz')
data_local = np.load('./dualmoon_data_local.npz')
local_size = data_local['chains'].shape[1]
global_size = data_global['chains'].shape[1]
n_loop = 20

class NormalMCMC(Scene):

    def add_graph(self, level):
        graph = ImplicitFunction(
            lambda x, y: dualmoon(np.array([x, y]))+level,
            color=BLUE,
            y_range=[-3,3],
            x_range=[-3,3],
        )
        return graph

    def construct(self):
        chain_number = 5
        graphs = []
        level_set = [15, 10, 5, 0]
        for i in range(len(level_set)):
            graphs.append(self.add_graph(level_set[i]))
            graphs[-1].set_opacity(0.2+0.2*i)
            graphs[-1].set_stroke(width=0.)
        text = Text("Normal MCMC", color=WHITE).shift(UP*3.5)
        self.play(Write(text))
        self.play(AnimationGroup(*[FadeIn(graph) for graph in graphs], lag_ratio=0.5))

        
        chain = data_local['chains'][chain_number,::int(local_size/n_loop)]

        init_pos = np.array([chain[0,0], chain[0,1], 0])
        final_pos = np.array([chain[-1,0], chain[-1,1], 0])

        walker = Dot(init_pos)
        proposal_Gaussian_inner = Circle(color=GREEN, radius=0.6, fill_opacity=0.4, stroke_width=0).move_to(init_pos)
        proposal_Gaussian_outer = Circle(color=GREEN, radius=1.0, fill_opacity=0.2, stroke_width=0).move_to(init_pos)
        arrow = Arrow(init_pos, np.array([chain[1,0],chain[1,1],0]), color=YELLOW, max_stroke_width_to_length_ratio=5).scale(10,scale_tips=True)
        red_arrow = Arrow(final_pos, np.array([chain[-1,0]-4.5, chain[-1,1],0]), color=WHITE, stroke_width=4)

        self.play(FadeIn(walker))
        self.wait(0.5)
        self.play(FadeIn(proposal_Gaussian_inner), FadeIn(proposal_Gaussian_outer))
        self.wait(0.5)

        self.play(GrowArrow(arrow))
        self.wait(0.5)
        self.play(Transform(arrow, Arrow(init_pos, init_pos, color=YELLOW, stroke_width=0)))
        self.wait(0.5)

        self.play(FadeOut(proposal_Gaussian_inner), FadeOut(proposal_Gaussian_outer))
        self.wait(0.5)

        for i in range(1,n_loop):
            self.play(walker.animate.move_to(np.array([chain[i][0], chain[i][1], 0])))

        self.play(GrowArrow(red_arrow))
        self.play(Indicate(red_arrow, color=RED,scale_factor=1))

nf_data = np.load("./dualmoon_nf_samples.npz",allow_pickle=True)['nf_samples_array']
class BuildingFlow(Scene):

    def add_graph(self, level, data):
        kde = gaussian_kde(data.T)
        graph = ImplicitFunction(
            lambda x, y: np.log(kde(np.array([x,y])))+level,
            color=GREEN,
            y_range=[-3,3],
            x_range=[-3,3],
        )
        return graph

    def construct(self):
        graphs = []
        level_set = [5, 3, 1, -1]
        for i in range(len(level_set)):
            graphs.append(self.add_graph(level_set[i],nf_data[0]))
            graphs[-1].set_opacity(0.2+0.2*i)
            graphs[-1].set_stroke(width=0.)
        text = Text("Training normalizing flow", color=WHITE).shift(UP*3.5)
        self.play(Write(text))
        self.play(AnimationGroup(*[FadeIn(graph) for graph in graphs], lag_ratio=0.5))



        dot_set = Group(*[Dot(np.array([nf_data[0][::100][i][0],nf_data[0][::100][i][1],0]),radius=0.1).set_z_index(10) for i in range(10)])
        self.play(FadeIn(dot_set,radius=0.1))
        for j in range(10):
            dot_set_new = Group(*[Dot(np.array([nf_data[1+2*j][::100][i][0],nf_data[1+2*j][::100][i][1],0]),radius=0.1).set_z_index(10) for i in range(10)])
            level_set = [7, 5, 3, 1]
            new_graphs = []
            for i in range(len(level_set)):
                new_graphs.append(self.add_graph(level_set[i],nf_data[1+2*j]))
                new_graphs[-1].set_opacity(0.2+0.2*i)
                new_graphs[-1].set_stroke(width=0.)
            self.play(FadeIn(dot_set_new))
            self.play(AnimationGroup(*[Transform(graphs[i],new_graphs[i]) for i in range(3)]))


class FlowMC(Scene):

    def add_graph(self, level):
        graph = ImplicitFunction(
            lambda x, y: dualmoon(np.array([x, y]))+level,
            color=BLUE,
            y_range=[-3,3],
            x_range=[-3,3],
        )
        return graph

    def add_NF(self, level, data):
        kde = gaussian_kde(data.T)
        graph = ImplicitFunction(
            lambda x, y: np.log(kde(np.array([x,y])))+level,
            color=GREEN,
            y_range=[-3,3],
            x_range=[-3,3],
        )
        return graph

    def construct(self):
        chain_number = 5
        graphs = []
        level_set = [15, 10, 5, 0]
        for i in range(len(level_set)):
            graphs.append(self.add_graph(level_set[i]))
            graphs[-1].set_opacity(0.2+0.2*i)
            graphs[-1].set_stroke(width=0.)
        text = Text("flowMC", color=WHITE).shift(UP*3.5)
        self.play(Write(text))
        self.play(AnimationGroup(*[FadeIn(graph) for graph in graphs], lag_ratio=0.5))

        NF_graphs = []
        level_set = [5, 3, 1, -1]
        for i in range(len(level_set)):
            NF_graphs.append(self.add_NF(level_set[i],nf_data[19]))
            NF_graphs[-1].set_opacity(0.2+0.2*i)
            NF_graphs[-1].set_stroke(width=0.)
        self.play(AnimationGroup(*[FadeIn(graph) for graph in NF_graphs]))

        chain = data_global['chains'][chain_number]
        steps_index = np.random.choice(np.where(chain[:,0]>0)[0],size=int(n_loop/4))
        steps_index = np.append(steps_index,np.random.choice(np.where(chain[:,0]<0)[0],size=int(3*n_loop/4)))
        np.random.shuffle(steps_index)
        print(chain[steps_index[0]])
        walker = Dot(np.array([chain[steps_index[0],0], chain[steps_index[0],1], 0]))
        self.play(FadeIn(walker))
        for i in range(1,n_loop-1):
            self.play(walker.animate.move_to(np.array([chain[steps_index[i],0], chain[steps_index[i],1], 0])))