from curses.ascii import CR
from venv import create
from manim import *
from sympy import sympify
from SRgraph import *
import numpy as np
from scipy.interpolate import interp1d

data = np.load('./GWTC3_m1_spectrum.npz')
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
        self.axes.y_range = [1e-6,6]
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

