from cProfile import run
from cmath import isnan
from nturl2path import pathname2url
from telnetlib import DO
from turtle import circle
from manim import *
from scipy.fftpack import shift
from scipy.interpolate import interp1d
import numpy as np

"""
Loading data
"""

def powerLaw(x,slope=-2,intercept=10):
    output = slope*x+intercept
    return output

def gaussian(x, mu=2.5, sigma=1, A=1):
    return A*np.exp(-(x - mu)**2/(2*sigma**2))

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
low = low.clip(0.,11)
high = high.clip(0.,11)

interp_median = interp1d(axis, median, bounds_error=False,fill_value=0)
interp_low = interp1d(axis, low, bounds_error=False,fill_value=0)
interp_high = interp1d(axis, high, bounds_error=False,fill_value=0)

GWTC3_m1pro = np.load('/home/kaze/Work/ManimAnimation/Backpop//GWTC3_m1pro.npz')
bins = GWTC3_m1pro['bin']
counts = GWTC3_m1pro['count']
bins = (bins - bins.min())/(bins.max()-bins.min())*5
counts = (counts-counts.min())/(counts.max()-counts.min())*10

interp_count = interp1d(bins, counts, bounds_error=False,fill_value=0)

"""
Scenes
"""
class ForwardModel(Scene):
    def construct(self):

        # Prepare objects

        self.distribution = Distribution(powerLaw,label=r'm_{1,\rm{ini}}')
        self.distribution_obs = Distribution(powerLaw,color=YELLOW).rotate(-PI/2).scale(0.5).shift(5*RIGHT).shift(0.5*UP)
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
        text_simulation = Tex("Evolve",font_size=40).scale(1.5).shift(3.5*UP)
        text_function = Tex(r"$f(m_1;\alpha = -2)$",font_size=30).scale(1.5).shift(2.5*UP)
        for i in range(n_binary-1,-1,-1):
            AnimationList.append(FadeOut(arrowList[i],shift=RIGHT,scale=0))
            AnimationList.append(Transform(binaryList[i],remnentList[i]))
        self.play(AnimationGroup(*[Create(text_simulation),Create(text_function)],lag_ratio=0.5),run_time=0.5)

        self.play(AnimationGroup(*[GrowArrow(arrowList[i]) for i in range(n_binary-1,-1,-1)],lag_ratio=0.2))
        self.play(Uncreate(text_simulation),Uncreate(text_function),AnimationGroup(*AnimationList,lag_ratio=0.2))
        self.play(AnimationGroup(*[FadeOut(binaryList[i],shift=RIGHT,scale=0) for i in range(n_binary-1,-1,-1)]),FadeIn(self.distribution_obs))
        self.play(Wiggle(self.distribution.graph))
        self.play(Wiggle(self.distribution_obs.graph))
        self.play(FadeOut(self.distribution),Transform(self.distribution_obs, self.distribution_obs.copy().rotate(PI/2).scale(2).shift(5*LEFT)))
        self.wait(0.5)

class CompareDistribution(Scene):
    def construct(self):
        text_simulation = Tex(r"$f(m_1;\alpha = -2)$",font_size=40).scale(1.5).shift(3.0*UP)
        self.distribution_theory = Distribution(powerLaw,color=YELLOW)
        self.distribution_median = Distribution(interp_median,with_axis=False,color=BLUE)
        low = self.distribution_median.axes.plot(interp_low, x_range=np.array([0,5,0.01]))
        high = self.distribution_median.axes.plot(interp_high, x_range=np.array([0,5,0.01]))
        area = self.distribution_median.axes.get_area(graph=low, x_range=[0,5], bounded_graph=high)
        self.add(self.distribution_theory)
        self.play(Write(text_simulation))
        self.wait(0.5)
        self.play(FadeIn(area),Create(self.distribution_median))
        self.wait(0.5)
        new_text =  Tex(r"$f(m_1;\alpha = -3)$",font_size=40).scale(1.5).shift(3.0*UP)
        self.play(Transform(self.distribution_theory, Distribution(lambda x: powerLaw(x,slope=-3,intercept=12),color=YELLOW)),
                Transform(text_simulation, new_text))
        new_text =  Tex(r"$f(m_1;\alpha = -1)$",font_size=40).scale(1.5).shift(3.0*UP)
        self.play(Transform(self.distribution_theory, Distribution(lambda x: powerLaw(x,slope=-1,intercept=8),color=YELLOW)),
                Transform(text_simulation, new_text))
        new_text =  Tex(r"$f(m_1;\alpha = -2)$",font_size=40).scale(1.5).shift(3.0*UP)
        self.play(Transform(self.distribution_theory, Distribution(lambda x: powerLaw(x,slope=-2,intercept=10),color=YELLOW)),
                Transform(text_simulation, new_text))
        self.wait(0.5)

class ProblemWithForwardModelling(Scene):
    def construct(self):

        self.distribution_final = Distribution(powerLaw,color=YELLOW)
        self.distribution_initial = Distribution(powerLaw,color=RED,label=r'm_{1,\rm{ini}}')
        self.play(Transform(self.distribution_final,self.distribution_final.copy().scale(0.5).shift(4*RIGHT)))
        self.play(Write(Tex("Final population",font_size=40).scale(1.5).shift(3.0*UP).shift(3.5*RIGHT)))
        self.play(Transform(self.distribution_initial,self.distribution_initial.copy().scale(0.5).shift(3*LEFT)))
        self.play(Write(Tex("Initial population",font_size=40).scale(1.5).shift(3.0*UP).shift(3*LEFT)))
        AnimationList = []
        AnimationList.append(Transform(self.distribution_initial,Distribution(lambda x: gaussian(x,mu=2,sigma=1,A=5),color=RED,label=r'm_{1,\rm{ini}}').scale(0.5).shift(3*LEFT)))
        AnimationList.append(Transform(self.distribution_final,Distribution(lambda x: gaussian(x,mu=2,sigma=1,A=5),color=YELLOW).scale(0.5).shift(4*RIGHT)))
        self.play(AnimationGroup(*AnimationList,lag_ratio=0.4))
        AnimationList = []
        AnimationList.append(Transform(self.distribution_initial.graph,ParametricFunction(normalize_elphant,color=RED).rotate(-PI/2).move_to(self.distribution_initial.axes.get_center()).scale(2)))
        AnimationList.append(Transform(self.distribution_final,Distribution(lambda x: gaussian(x,mu=2,sigma=0.2,A=9),color=YELLOW).scale(0.5).shift(4*RIGHT)))
        self.play(AnimationGroup(*AnimationList,lag_ratio=0.4))
        AnimationList = []
        AnimationList.append(Transform(self.distribution_initial.graph,ParametricFunction(lambda t: normalize_elphant(t,70-30j),color=RED).rotate(-PI/2).move_to(self.distribution_initial.axes.get_center()).scale(2)))
        AnimationList.append(Transform(self.distribution_final,Distribution(lambda x: gaussian(x,mu=2,sigma=0.6,A=7),color=YELLOW).scale(0.5).shift(4*RIGHT)))
        self.play(AnimationGroup(*AnimationList,lag_ratio=0.4))

        self.wait(0.5)



class BackPop(Scene):
    def construct(self):
        remnentList = []
        binaryList = []
        arrowList = []

        n_binary = 3
        for i in range(n_binary-1,-1,-1):
            remnentList.append(Binary(radius=0, center = np.array([2,i-1,0]), trail_length=1).set_color(interpolate_color(BLUE, RED, i/(n_binary-1))))
            for j in range(3):
                binaryList.append(Binary(radius=0.1,center = np.array([-2,j*2+i*0.66-2.66,0]), trail_length=1).set_color(interpolate_color(BLUE, RED, (3*j+i)/(3*n_binary-1))))
        for i in range(n_binary-1,-1,-1):
            for j in range(3):
                arrowList.append(Arrow (remnentList[i],binaryList[3*i+j].center,buff=0.1).set_color([remnentList[i].get_color(),binaryList[3*i+j].get_color()]))




        self.distribution = Distribution(interp_count,label=r'm_{1,\rm{ini}}').rotate(PI/2).scale(0.5).shift(5*LEFT)
        self.distribution_median = Distribution(interp_median,color=BLUE)
        low = self.distribution_median.axes.plot(interp_low, x_range=np.array([0,5,0.01]))
        high = self.distribution_median.axes.plot(interp_high, x_range=np.array([0,5,0.01]))
        area = self.distribution_median.axes.get_area(graph=low, x_range=[0,5], bounded_graph=high)
        group = VGroup(area,self.distribution_median)
        self.wait(0.5)
        self.play(Transform(group, group .copy().rotate(-PI/2).scale(0.5).shift(5*RIGHT) ))

        graph_points = group[1].graph.get_all_points()
        self.play(*[GrowFromPoint(remnentList[i], graph_points[np.linspace(0,graph_points.shape[0]-1,n_binary).astype(int)][i]) for i in range(n_binary-1,-1,-1)])
        self.wait(0.5)
        AnimationList = []
        for j in range(3):
            for i in range(n_binary-1,-1,-1):
                AnimationList.append(GrowArrow(arrowList[i+3*(n_binary-j-1)]))
                AnimationList.append(FadeIn(binaryList[i+3*j]))
        self.play(AnimationGroup(*AnimationList[:(n_binary*2)],lag_ratio=0.2))

        text_function = Tex(r"$f^{-1}(f(m_{1,1};\alpha_1))$",font_size=40).scale(1).shift(3.5*UP)
        indicate_arrow = Arrow(text_function.get_center(),arrowList[8].get_center(),buff=0.3)
        self.play(Write(text_function),GrowArrow(indicate_arrow),run_time=0.5)
        self.wait(0.5)
        new_text =  Tex(r"$f^{-1}(f(m_{1,2};\alpha_2))$",font_size=40).scale(1).shift(3.5*UP)
        new_indicate_arrow = Arrow(text_function.get_center(),arrowList[7].get_center(),buff=0.3)
        self.play(Transform(text_function, new_text),Transform(indicate_arrow, new_indicate_arrow))
        self.wait(0.5)
        new_text =  Tex(r"$f^{-1}(f(m_{1,3};\alpha_3))$",font_size=40).scale(1).shift(3.5*UP)
        new_indicate_arrow = Arrow(text_function.get_center(),arrowList[6].get_center(),buff=0.3)
        self.play(Transform(text_function, new_text),Transform(indicate_arrow, new_indicate_arrow))
        self.wait(0.5)
        self.play(Uncreate(text_function),Uncreate(indicate_arrow),run_time=0.5)

        self.wait(0.5)
        self.play(AnimationGroup(*AnimationList[(n_binary*2):],lag_ratio=0.2))
        self.wait(0.5)
        AnimationList = []
        for j in range(3):
            AnimationList.append(FadeOut(remnentList[j],shift=0.1*LEFT))
            for i in range(n_binary-1,-1,-1):
                AnimationList.append(Uncreate(arrowList[3*j+i].set_points(arrowList[3*j+i].get_points()[::-1])))
        self.play(AnimationGroup(*AnimationList))
        self.wait(0.5)
        self.play(AnimationGroup(*[FadeOut(binaryList[i],shift=LEFT,scale=0) for i in range(3*n_binary-1,-1,-1)]),FadeIn(self.distribution))
        self.wait(0.5)
        self.play(FadeOut(group),Transform(self.distribution, self.distribution.copy().rotate(-PI/2).scale(2).shift(5*RIGHT)))
        self.wait(0.5)


"""
Helper functions
"""

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
    def __init__(self, function, with_axis=True, color=RED,label='m_{1}'):
        super().__init__()
        self.axes = Axes(x_range=[0,5], y_range=[0,10,10],axis_config={"include_tip": False})
        axis = np.linspace(0.1,5,500)
        self.graph = self.axes.plot_line_graph(x_values=axis,y_values=function(axis),line_color=color,add_vertex_dots=False, stroke_width=4,)
        self.with_axis = with_axis
        if with_axis:
            y_label = self.axes.get_y_axis_label(r"p("+label+")", edge=LEFT, direction=LEFT).rotate(PI/2).shift(0.5*LEFT)
            x_label = self.axes.get_x_axis_label(r""+label, edge=DOWN, direction=DOWN,buff=10)
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

# elephant parameters
p1, p2, p3, p4 = (50 - 30j, 18 +  8j, 12 - 10j, -14 - 60j )
p5 = 40 + 20j # eyepiece

def fourier(t, C):
    f = np.zeros(t.shape)
    A, B = C.real, C.imag
    for k in range(len(C)):
        f = f + A[k]*np.cos(k*t) + B[k]*np.sin(k*t)
    return f

def elephant(t,p1=50-30j):
    npar = 6
    Cx = np.zeros((npar,), dtype='complex')
    Cy = np.zeros((npar,), dtype='complex')

    Cx[1] = p1.real*1j
    Cx[2] = p2.real*1j
    Cx[3] = p3.real
    Cx[5] = p4.real

    Cy[1] = p4.imag + p1.imag*1j
    Cy[2] = p2.imag*1j
    Cy[3] = p3.imag*1j

    x = fourier(t,Cx)
    y = fourier(t,Cy)

    return np.array((x,y,0))


        
def normalize_elphant(t,p1=50-30j):
    t_range = np.linspace(0,2*np.pi,100)
    x_min = 1000
    x_max = -1000
    y_min = 1000
    y_max = -1000
    for i in range(100):
        elephant_unormalize = elephant(t_range[i],p1)
        if x_min > elephant_unormalize[0]:
            x_min = elephant_unormalize[0]
        if x_max < elephant_unormalize[0]:
            x_max = elephant_unormalize[0]
        if y_min > elephant_unormalize[1]:
            y_min = elephant_unormalize[1]
        if y_max < elephant_unormalize[1]:
            y_max = elephant_unormalize[1]
    value = elephant(t*2*np.pi,p1)
    output = np.array(((value[0]-x_min)/(x_max-x_min),(value[1]-y_min)/(y_max-y_min),0))
    return output