from cProfile import run
from cmath import isnan
from nturl2path import pathname2url
from telnetlib import DO
from turtle import circle
from manim import *
from scipy.interpolate import interp1d
import numpy as np

def powerLaw(x,slope=-2,intercept=10):
    output = slope*x+intercept
    return output

GWTC3_m1_data = np.load('/home/kaze/Work/ManimAnimation/Backpop/GWTC3_m1_pp.npz')
axis = (GWTC3_m1_data['axis']-2.)/98.*5
median =  np.log10(GWTC3_m1_data['pm1_med']+0.0001)
y_min = median.min()
y_max = median.max()
low = np.log10(GWTC3_m1_data['pm1_low']+0.0001)
high = np.log10(GWTC3_m1_data['pm1_high']+0.0001)
median =  (median-y_min)/(y_max-y_min)*10
low = (low-y_min)/(y_max-y_min)*10
high = (high-y_min)/(y_max-y_min)*10

interp_median = interp1d(axis, median, bounds_error=False,fill_value=0)
interp_low = interp1d(axis, low, bounds_error=False,fill_value=0)
interp_high = interp1d(axis, high, bounds_error=False,fill_value=0)

class ForwardModel(Scene):
    def construct(self):

        # Prepare objects

        self.distribution = Distribution(powerLaw)
        self.distribution_obs = Distribution(powerLaw).rotate(-PI/2).scale(0.5).shift(5*RIGHT)
        binaryList = []
        remnentList = []
        arrowList = []
        n_binary = 5
        for i in range(n_binary):
            binaryList.append(Binary(center = np.array([-2,i-2.5,0]), trail_length=1).set_color(interpolate_color(RED, BLUE, i/4)))
            remnentList.append(Binary(radius=0, center = np.array([2,i-2.5,0]), trail_length=1).set_color(interpolate_color(RED, BLUE, i/4)))
            arrowList.append(Arrow(binaryList[i].center, remnentList[i],buff=1).set_color(interpolate_color(RED, BLUE, i/4)))

        # Create initial distribution and rotate it

        self.play(Create(self.distribution))
        self.wait(0.5)
        self.play(Transform(self.distribution, self.distribution.copy().rotate(PI/2).scale(0.5).shift(5*LEFT)))

        # Sample binaries from the distribution
        graph_points = self.distribution.graph.get_all_points()
        self.play(*[GrowFromPoint(binaryList[i], graph_points[np.linspace(0,graph_points.shape[0]-1,n_binary).astype(int)][i]) for i in range(n_binary)])

        # Rotate binaries
        for i in range(n_binary):
            binaryList[i].trail_length = 60
        self.play(AnimationGroup(*[Rotate(binaryList[i]) for i in range(n_binary)]),run_time=2)
        for i in range(n_binary):
            binaryList[i].trail_length = 1

        # Evolve binaries        
        AnimationList = []
        text_simulation = Tex("Evolve",font_size=40).scale(1.5).shift(2.5*UP)
        for i in range(n_binary-1,-1,-1):
            AnimationList.append(FadeOut(arrowList[i],shift=RIGHT,scale=0))
            AnimationList.append(Transform(binaryList[i],remnentList[i]))
        self.play(AnimationGroup(*[GrowArrow(arrowList[i]) for i in range(n_binary-1,-1,-1)],lag_ratio=0.2),Create(text_simulation))
        self.play(Uncreate(text_simulation),AnimationGroup(*AnimationList,lag_ratio=0.2))
        self.play(AnimationGroup(*[FadeOut(binaryList[i],shift=RIGHT,scale=0) for i in range(n_binary-1,-1,-1)]),FadeIn(self.distribution_obs))
        self.play(FadeOut(self.distribution),Transform(self.distribution_obs, self.distribution_obs.copy().rotate(PI/2).scale(2).shift(5*LEFT)))
        self.wait(0.5)

class CompareDistribution(Scene):
    def construct(self):
        text_simulation = Tex(r"$f(m_1;\alpha = -2)$",font_size=40).scale(1.5).shift(3.0*UP)
        self.distribution_theory = Distribution(powerLaw)
        self.distribution_median = Distribution(interp_median,with_axis=False,color=BLUE)
        low = self.distribution_median.axes.plot(interp_low, x_range=np.array([0,5,0.01]))
        high = self.distribution_median.axes.plot(interp_high, x_range=np.array([0,5,0.01]))
        area = self.distribution_median.axes.get_area(graph=low, x_range=[0,5], bounded_graph=high)
        self.play(Create(self.distribution_theory),Create(self.distribution_median))
        self.play(FadeIn(area)) 
        self.play(Write(text_simulation))
        self.wait(0.5)
        new_text =  Tex(r"$f(m_1;\alpha = -3)$",font_size=40).scale(1.5).shift(3.0*UP)
        self.play(Transform(self.distribution_theory, Distribution(lambda x: powerLaw(x,slope=-3,intercept=12))),
                Transform(text_simulation, new_text))
        new_text =  Tex(r"$f(m_1;\alpha = -1)$",font_size=40).scale(1.5).shift(3.0*UP)
        self.play(Transform(self.distribution_theory, Distribution(lambda x: powerLaw(x,slope=-1,intercept=8))),
                Transform(text_simulation, new_text))
        new_text =  Tex(r"$f(m_1;\alpha = -2)$",font_size=40).scale(1.5).shift(3.0*UP)
        self.play(Transform(self.distribution_theory, Distribution(lambda x: powerLaw(x,slope=-2,intercept=10))),
                Transform(text_simulation, new_text))
        self.wait(0.5)



class Binary(VGroup):
    def __init__(self,radius=0.2,center: np.array=np.array([0,0,0]),trail_length = 0,final_center = None):
        super().__init__()
        self.center = center
        self.trail_length = trail_length
        self.dot1 = Dot().move_to(center)
        self.dot2 = Dot().move_to(center)
        self.path1 = VMobject()
        self.path2 = VMobject()

        self.dot1.shift(radius*UP)
        self.dot2.shift(radius*DOWN)            

        def path1_updater(path):
            previous_path = path.copy()
            previous_path.add_points_as_corners([self.dot1.get_center()])
            previous_path.points = previous_path.points[-self.trail_length:]

            path.become(previous_path)

        def path2_updater(path):
            previous_path = path.copy()
            previous_path.add_points_as_corners([self.dot2.get_center()])
            previous_path.points = previous_path.points[-self.trail_length:]
            path.become(previous_path)

        self.path1.set_points_as_corners([self.dot1.get_center(), self.dot1.get_center()])
        self.path2.set_points_as_corners([self.dot2.get_center(), self.dot2.get_center()])
        self.path1.add_updater(path1_updater)
        self.path2.add_updater(path2_updater)

        self.add(self.dot1,self.dot2,self.path1,self.path2)

    @override_animation(Rotate)
    def _rotate(self,**kwargs):
        dot1_rotate = Rotate(self.dot1,angle=6*PI,about_point=self.get_center(),rate_func=linear,)
        dot2_rotate = Rotate(self.dot2,angle=6*PI,about_point=self.get_center(),rate_func=linear,)        
        return AnimationGroup(dot1_rotate,dot2_rotate)


class Distribution(VGroup):
    def __init__(self, function, with_axis=True, color=RED):
        super().__init__()
        self.axes = Axes(x_range=[0,5], y_range=[0,10,10],axis_config={"include_tip": False})
        axis = np.linspace(0.1,5,500)
        self.graph = self.axes.plot_line_graph(x_values=axis,y_values=function(axis),line_color=color,add_vertex_dots=False, stroke_width=4,)
        self.with_axis = with_axis
        if with_axis:
            y_label = self.axes.get_y_axis_label(r"p(m_{1})", edge=LEFT, direction=LEFT).rotate(PI/2).shift(0.5*LEFT)
            x_label = self.axes.get_x_axis_label(r"m_{1}", edge=DOWN, direction=DOWN,buff=10)
            self.grid_labels = VGroup(x_label, y_label)
            self.add(self.axes,self.graph, self.grid_labels)
        else:
            self.add(self.axes,self.graph)

    @override_animation(Create)
    def _create(self,**kwargs):
        if self.with_axis:
            return AnimationGroup(Create(self.axes),Create(self.graph),Create(self.grid_labels))
        else:
            return AnimationGroup(Create(self.axes),Create(self.graph))
