from curses.ascii import CR
from venv import create
from manim import *
from sympy import sympify
from SRgraph import *
import numpy as np
from scipy.interpolate import interp1d
from scipy.stats import gaussian_kde

data = np.load('./vamana_m1_spectrum.npz')
m1_axis = data['axis']
pm1_med = data['pm1_med']
pm1_med[pm1_med<1e-6] = 1e-6
pm1_low = data['pm1_low']
pm1_low[pm1_low<1e-6] = 1e-6
pm1_high = data['pm1_high']
pm1_high[pm1_high<1e-6] = 1e-6
pm1_med = interp1d(m1_axis,pm1_med,bounds_error=False,fill_value=1e-12)
pm1_low = interp1d(m1_axis,pm1_low,bounds_error=False,fill_value=1e-12)
pm1_high = interp1d(m1_axis,pm1_high,bounds_error=False,fill_value=1e-12)

data = np.load('./GWTC3_LVK_posterior_m1.npz')
m1_samples = data['data']
kde_array = []
for i in range(len(m1_samples)):
    kde_array.append(gaussian_kde(m1_samples[i]))

class GW_population(Scene):
    def construct(self):
        self.axes = Axes(x_range=[0.01,100,10], y_range=[1e-6,5e-1,0.1],axis_config={"include_tip": True, "include_numbers": True}).scale(0.9)
        posterior_array = [self.axes]
        for i in range(len(m1_samples)):
            m1_axis = np.linspace(m1_samples[i].min()*0.8,min(m1_samples[i].max()*1.2,100),500)
            line = self.axes.plot_line_graph(x_values=m1_axis,y_values=kde_array[i](m1_axis), add_vertex_dots=False, line_color= WHITE)
            line.set_stroke(opacity=0.3)
            posterior_array.append(line)
        self.plot_group = VGroup(*posterior_array).shift(UP*0.5,RIGHT*0.2)
        y_label = self.axes.get_y_axis_label(r"p(m_1)", edge=LEFT, direction=LEFT, buff=1).rotate(PI/2).shift(0.6*LEFT)
        x_label = self.axes.get_x_axis_label(r"m_1", edge=DOWN, direction=DOWN,buff=10).shift(0.8*UP).shift(0.4*LEFT)
        self.grid_labels = VGroup(x_label, y_label).shift(RIGHT*0.5).shift(DOWN*0.5)
        self.play(Create(self.plot_group[0]),Create(self.grid_labels))
        self.play(Create(posterior_array[1]),run_time=1)
        animation_group = []
        for i in range(78):
            animation_group.append(Create(posterior_array[2+i]))
        self.play(AnimationGroup(*animation_group,run_time=1,lag_ratio=0.1,rate_func=rush_into))
        self.wait()

class PhenomenologicalModelling(Scene):
    def construct(self):
        self.axes = Axes(x_range=[0,2.1,1], y_range=[-4,1,1],axis_config={"include_tip": True, "include_numbers": True, "scaling": LogBase(custom_labels=True)},
                        ).scale(0.9)
        power_law = lambda x, A, a: A**a * x**(a) 
        power_law_plus_gaussian = lambda x, A1, A2, a, sigma, mu: power_law(x,A1,a) + A2*np.exp(-((x-mu)/sigma)**2)
        power_law_plus_gaussian_plus_gaussian = lambda x, A1, A2, a, sigma, mu, A3, sigma2, mu2: power_law_plus_gaussian(x,A1,A2,a,sigma,mu) + A3*np.exp(-((x-mu2)/sigma2)**2)
        self.power_law = self.axes.plot(lambda x : power_law(x, 1, -2), x_range=[0,2.1,0.1])
        self.add(self.axes, self.power_law)
        self.play(Transform(self.power_law,self.axes.plot(lambda x : power_law(x, 0.5, -3), x_range=[0,2.1,0.1])))
        self.play(Transform(self.power_law,self.axes.plot(lambda x : power_law(x, 5, -1), x_range=[0,2.1,0.1])))
        self.play(Transform(self.power_law,self.axes.plot(lambda x : power_law(x, 1, -2), x_range=[0,2.1,0.1])))
        self.play(Transform(self.power_law,self.axes.plot(lambda x : power_law_plus_gaussian(x, 1, 1e-2, -2, 5, 30), x_range=[0,2.1,0.01])))
        self.play(Transform(self.power_law,self.axes.plot(lambda x : power_law_plus_gaussian_plus_gaussian(x, 1, 5e-3, -2, 5, 30, 5e-1, 1, 5), x_range=[0,2.1,0.01])))

class SRMain(Scene):
    def construct(self):
        equation1 = sympify('(((x1 * x1) - 2.0) + (cos(x2)))')
        equation2 = sympify('(((x1 * x1) - 2.0) + (cos(x2) * 3.0))')
        G1 = get_graph(equation1)
        G2 = get_graph(equation2)
        G = get_manim_graph(nx.compose(nx.intersection(G1,G2),G2))
        self.add(G)
        # self.play(Write(G1),run_time=2)
        # self.play(ReplacementTransform(G1, G2), run_time=2)
        # self.wait(1)


class FitMassFunction(Scene):
    def construct(self):
        self.axes = Axes(x_range=[0,100,10], y_range=[-6,1],axis_config={"include_tip": True, "include_numbers": True},y_axis_config={"scaling": LogBase(10)})
        median = self.axes.plot_line_graph(x_values=m1_axis, y_values=pm1_med(m1_axis), line_color=BLUE, add_vertex_dots=False, stroke_width = 4)
        low = self.axes.plot(pm1_low,x_range=np.array([1,100,0.1]))
        high = self.axes.plot(pm1_high,x_range=np.array([1,100,0.1]))
        area = self.axes.get_area(graph=low, x_range=[0,100], bounded_graph=high)
        self.plot = VGroup(self.axes, median, area).scale(0.9).shift(UP*0.3).shift(RIGHT*0.5)
        y_label = self.axes.get_y_axis_label(r"p(m_1)", edge=LEFT, direction=LEFT, buff=1).rotate(PI/2).shift(0.6*LEFT)
        x_label = self.axes.get_x_axis_label(r"m_1", edge=DOWN, direction=DOWN,buff=10).shift(0.8*UP).shift(0.4*LEFT)
        self.grid_labels = VGroup(x_label, y_label).shift(RIGHT*0.5).shift(DOWN*0.5)
        self.add(self.plot, self.grid_labels)
        # self.play(Create(self.axes), Create(median), FadeIn(area), Write(self.grid_labels))

