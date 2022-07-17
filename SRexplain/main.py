from asyncio import WriteTransport
from curses.ascii import CR
from venv import create
from manim import *
from sympy import symmetric_poly, sympify, lambdify
from SRgraph import *
import numpy as np
import sympy
from sympy import preorder_traversal, Float 
from scipy.interpolate import interp1d
from scipy.stats import gaussian_kde

data = np.load('/home/kaze/Work/ManimAnimation/SRexplain/vamana_m1_spectrum.npz')
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

data = np.load('/home/kaze/Work/ManimAnimation/SRexplain/GWTC3_LVK_posterior_m1.npz')
m1_samples = data['data']
kde_array = []
for i in range(len(m1_samples)):
    kde_array.append(gaussian_kde(m1_samples[i]))

class GW_population(Scene):
    def construct(self):
        self.axes = Axes(x_range=[0.01,100,10], y_range=[1e-6,5e-1,0.1],axis_config={"include_tip": True, "include_numbers": True}).scale(0.9)
        y_label = self.axes.get_y_axis_label(r"p(m_1)", edge=LEFT, direction=LEFT, buff=1).rotate(PI/2).shift(0.9*LEFT)
        x_label = self.axes.get_x_axis_label(r"m_1", edge=DOWN, direction=DOWN,buff=10).shift(0.6*UP).shift(0.6*LEFT)
        self.grid_labels = VGroup(x_label, y_label).shift(RIGHT*0.5).shift(DOWN*0.5)
        self.play(Create(self.axes),Create(self.grid_labels))

        posterior_array = []
        for i in range(len(m1_samples)):
            m1_axis = np.linspace(m1_samples[i].min()*0.8,min(m1_samples[i].max()*1.2,100),500)
            line = self.axes.plot_line_graph(x_values=m1_axis,y_values=kde_array[i](m1_axis), add_vertex_dots=False, line_color= WHITE)
            line.set_stroke(opacity=0.3)
            posterior_array.append(line)
        self.plot_group = VGroup(*posterior_array)
        self.play(Create(posterior_array[0]),run_time=1)
        animation_group = []
        for i in range(78):
            animation_group.append(Create(posterior_array[1+i]))
        self.play(AnimationGroup(*animation_group,run_time=1,lag_ratio=0.1,rate_func=rush_into))
        self.wait()
        self.play(*[Uncreate(posterior_array[i]) for i in range(len(posterior_array))])

class PhenomenologicalModelling(Scene):
    def construct(self):

        self.axes2 = Axes(x_range=[0.01,100,10], y_range=[1e-6,5e-1,0.1],axis_config={"include_tip": True, "include_numbers": True}).scale(0.9)

        self.axes = Axes(x_range=[0,2.1,1], y_range=[-4,1,1],axis_config={"include_tip": True, "include_numbers": True, "scaling": LogBase(custom_labels=True)},
                        ).scale(0.9)
        y_label = self.axes.get_y_axis_label(r"p(m_1)", edge=LEFT, direction=LEFT, buff=1).rotate(PI/2).shift(0.9*LEFT)
        x_label = self.axes.get_x_axis_label(r"m_1", edge=DOWN, direction=DOWN,buff=10).shift(0.6*UP).shift(0.6*LEFT)
        self.grid_labels = VGroup(x_label, y_label).shift(RIGHT*0.5).shift(DOWN*0.5)
        self.add(self.axes2, self.grid_labels)
        self.play(Transform(self.axes2,self.axes))
        
        power_law = lambda x, A, a: A**a * x**(a) 
        power_law_plus_gaussian = lambda x, A1, A2, a, sigma, mu: power_law(x,A1,a) + A2*np.exp(-((x-mu)/sigma)**2)
        power_law_plus_gaussian_plus_gaussian = lambda x, A1, A2, a, sigma, mu, A3, sigma2, mu2: power_law_plus_gaussian(x,A1,A2,a,sigma,mu) + A3*np.exp(-((x-mu2)/sigma2)**2)
        self.power_law = self.axes.plot(lambda x : power_law(x, 1, -2), x_range=[0,2.1,0.1])
        self.play(Create(self.power_law))
        self.play(Transform(self.power_law,self.axes.plot(lambda x : power_law(x, 0.5, -3), x_range=[0,2.1,0.1])))
        self.play(Transform(self.power_law,self.axes.plot(lambda x : power_law(x, 5, -1), x_range=[0,2.1,0.1])))
        self.play(Transform(self.power_law,self.axes.plot(lambda x : power_law(x, 1, -2), x_range=[0,2.1,0.1])))
        self.play(Transform(self.power_law,self.axes.plot(lambda x : power_law_plus_gaussian(x, 1, 1e-2, -2, 5, 30), x_range=[0,2.1,0.01])))
        self.play(Transform(self.power_law,self.axes.plot(lambda x : power_law_plus_gaussian_plus_gaussian(x, 1, 5e-3, -2, 5, 30, 5e-1, 1, 5), x_range=[0,2.1,0.01])))
        self.play(Uncreate(self.power_law))


def Gaussian(x, A, mu, sigma):
    return A*np.exp(-((x-mu)/sigma)**2)
class FitMassFunction(Scene):

    def construct(self):

        def plot_gaussian(axes, gaussian_list, x_axis, A, mu, sigma):
            y = Gaussian(x_axis, A, mu, sigma)
            y[y<1e-6] = 1e-6
            line = axes.plot_line_graph(x_values=x_axis,y_values=y,stroke_width=3,add_vertex_dots=False,line_color=GRAY_A)
            line.set_stroke(opacity=0.7)
            gaussian_list.append(line)
            return gaussian_list


        self.axes2 = Axes(x_range=[0,2.1,1], y_range=[-4,1,1],axis_config={"include_tip": True, "include_numbers": True, "scaling": LogBase(custom_labels=True)},
                        ).scale(0.9)
        self.axes = Axes(x_range=[0,100,10], y_range=[-6,1],axis_config={"include_tip": True, "include_numbers": True},y_axis_config={"scaling": LogBase(10)}).scale(0.9)
        y_label = self.axes.get_y_axis_label(r"p(m_1)", edge=LEFT, direction=LEFT, buff=1).rotate(PI/2).shift(0.9*LEFT)
        x_label = self.axes.get_x_axis_label(r"m_1", edge=DOWN, direction=DOWN,buff=10).shift(0.6*UP).shift(0.6*LEFT)
        self.grid_labels = VGroup(x_label, y_label).shift(RIGHT*0.5).shift(DOWN*0.5)
        self.add(self.axes2, self.grid_labels)
        self.play(Transform(self.axes2,self.axes))
        


        median = self.axes.plot_line_graph(x_values=m1_axis, y_values=pm1_med(m1_axis), line_color=BLUE, add_vertex_dots=False, stroke_width = 4)
        low = self.axes.plot(pm1_low,x_range=np.array([1,100,0.1]))
        high = self.axes.plot(pm1_high,x_range=np.array([1,100,0.1]))
        area = self.axes.get_area(graph=low, x_range=[0,100], bounded_graph=high)
        self.gaussians = []
        x_axis = np.arange(0,100,0.1)
        self.gaussians = plot_gaussian(self.axes, self.gaussians, x_axis, 1.4, 7.5, 1.3)
        self.gaussians = plot_gaussian(self.axes, self.gaussians, x_axis, 6.8, 9.8, 1.3)
        self.gaussians = plot_gaussian(self.axes, self.gaussians, x_axis, 0.4, 17, 4)
        self.gaussians = plot_gaussian(self.axes, self.gaussians, x_axis, 0.25, 31, 8)
        self.gaussians = plot_gaussian(self.axes, self.gaussians, x_axis, 0.009, 38, 30)

        self.model = MathTex(r"p(m_1) \propto \sum_i f_i\mathcal{N}(m_1;\mu_i,\sigma_i)",font_size=40).shift(3*RIGHT,2*UP)
        self.wait(0.5)
        self.play(Write(self.model))
        self.wait(0.5)
        self.play(Create(median), FadeIn(area))
        self.wait(0.5)
        self.play(*[FadeIn(self.gaussians[i]) for i in range(len(self.gaussians))])
        self.wait(0.5)
        
class SRMain(Scene):
    def construct(self):
        equation1 = sympify('x1 + 2')
        equation2 = sympify('x1 + 2 * sin(x1)')
        self.tex1 = MathTex(r"x_1 + 2",font_size=40,
                    substrings_to_isolate=["+"]).shift(5.5*LEFT)
        self.tex2 = MathTex(r"x_1 + 2 \sin{x_1}",font_size=40,
                    substrings_to_isolate=["+","\sin{x_1}"]).shift(5.5*LEFT)
        G1 = get_graph(equation1)
        G2 = get_graph(equation2)
        G1_manim = get_manim_graph(G1).shift(1.5*UP, 2.5*LEFT)
        G2_manim = get_manim_graph(G2).shift(2.5*LEFT)

        self.axes = Axes(x_range=[0,10], y_range=[0,12],axis_config={"include_tip": True, "include_numbers": True}).scale(0.9)
        y_label = self.axes.get_y_axis_label(r"y", edge=LEFT, direction=LEFT, buff=1).rotate(PI/2).shift(1*LEFT)
        x_label = self.axes.get_x_axis_label(r"x", edge=DOWN, direction=DOWN,buff=10).shift(0.8*UP).shift(0.4*LEFT)
        self.grid_labels = VGroup(x_label, y_label).shift(RIGHT*0.5).shift(DOWN*0.5)
        x_axis = np.linspace(0,9,100)
        data_axis = np.linspace(0,9,30)
        data = lambdify(list(equation2.free_symbols),equation2)(data_axis) + np.random.normal(0,0.6,30)
        self.function1 = self.axes.plot_line_graph(x_values = x_axis,y_values = lambdify(list(equation1.free_symbols),equation1)(x_axis),stroke_width=3,add_vertex_dots=False,line_color=WHITE).scale(0.5).shift(4*RIGHT)
        self.function2 = self.axes.plot_line_graph(x_values = x_axis,y_values = lambdify(list(equation2.free_symbols),equation2)(x_axis),stroke_width=3,add_vertex_dots=False,line_color=YELLOW).scale(0.5).shift(4*RIGHT)
        self.data = self.axes.plot_line_graph(x_values = data_axis,y_values = data,stroke_width=0, ).scale(0.5).shift(4*RIGHT)
        self.plot_group = VGroup(self.grid_labels,self.axes).scale(0.5).shift(4*RIGHT)


        self.play(Write(self.tex1),run_time=0.5)
        # self.play(Write(G1_manim))
        self.play(FadeIn(G1_manim,shift=RIGHT))
        self.play(Create(self.plot_group),Create(self.data))
        self.play(Create(self.function1))
        self.play(Indicate(self.tex1.submobjects[1])
                    ,Indicate(G1_manim.vertices['Add1']))
        self.play(Transform(self.function1,self.function2),ReplacementTransform(G1_manim,G2_manim),Transform(self.tex1,self.tex2))
        
        # self.play(ReplacementTransform(get_manim_graph(G1), get_manim_graph(G2)), run_time=2)
        self.wait(1)

class FittingGWwithSR(Scene):

    def round_expression(self, ex1):
        ex2 = ex1
        for a in preorder_traversal(ex1):
            if isinstance(a, Float):
                ex2 = ex2.subs(a, round(a, 2))
        return ex2

    def construct(self):

        Gauss =  lambda x: sympy.exp(-(x**2))
        Cond = lambda x, y: sympy.Piecewise((0, x < 0), (y, True))

        pysr_10 = sympify('3.72*(Cond(M-9.27,0.9**M)+Gauss(0.52*M-4.85))')
        pysr_15 = sympify('3.89*((Gauss(0.19*M-6.54)+0.45)*Cond(M-9.12,0.91**M)+Gauss(0.5*M-4.8))')
        pysr_30 = sympify('(Cond(M-9.42,0.62*0.9**M)+1.44*Gauss(0.51*M-4.88))*(5.11*Gauss(0.06*M-4.67)+7.82*Gauss(0.17*M-5.86)+3.26)')

        self.pysr_equation10 = lambdify(list(pysr_10.free_symbols),pysr_10,modules={"Gauss":Gauss,"Cond":Cond})
        self.pysr_equation15 = lambdify(list(pysr_15.free_symbols),pysr_15,modules={"Gauss":Gauss,"Cond":Cond})
        self.pysr_equation30 = lambdify(list(pysr_30.free_symbols),pysr_30,modules={"Gauss":Gauss,"Cond":Cond})

        label1 = sympy.latex(self.round_expression(pysr_10))
        label1 = label1.replace('operatorname','rm')
        label1 = label1.replace('&','\&')
        self.label1 = MathTex(label1).shift(3*UP).scale(0.5)

        label2 = sympy.latex(self.round_expression(pysr_15))
        label2 = label2.replace('operatorname','rm')
        label2 = label2.replace('&','\&')
        self.label2 = MathTex(label2).shift(3*UP).scale(0.5)

        label3 = sympy.latex(self.round_expression(pysr_30))
        label3 = label3.replace('operatorname','rm')
        label3 = label3.replace('&','\&')
        self.label3 = MathTex(label3).shift(3*UP).scale(0.5)

        def plot_gaussian(axes, gaussian_list, x_axis, A, mu, sigma):
            y = Gaussian(x_axis, A, mu, sigma)
            y[y<1e-6] = 1e-6
            line = axes.plot_line_graph(x_values=x_axis,y_values=y,stroke_width=3,add_vertex_dots=False,line_color=GRAY_A)
            line.set_stroke(opacity=0.7)
            gaussian_list.append(line)
            return gaussian_list


        self.axes = Axes(x_range=[0,100,10], y_range=[-6,1],axis_config={"include_tip": True, "include_numbers": True},y_axis_config={"scaling": LogBase(10)}).scale(0.9)
        y_label = self.axes.get_y_axis_label(r"p(m_1)", edge=LEFT, direction=LEFT, buff=1).rotate(PI/2).shift(0.9*LEFT)
        x_label = self.axes.get_x_axis_label(r"m_1", edge=DOWN, direction=DOWN,buff=10).shift(0.6*UP).shift(0.6*LEFT)
        self.grid_labels = VGroup(x_label, y_label).shift(RIGHT*0.5).shift(DOWN*0.5)
        self.add(self.axes, self.grid_labels)

        median = self.axes.plot_line_graph(x_values=m1_axis, y_values=pm1_med(m1_axis), line_color=BLUE, add_vertex_dots=False, stroke_width = 4)
        low = self.axes.plot(pm1_low,x_range=np.array([1,100,0.1]))
        high = self.axes.plot(pm1_high,x_range=np.array([1,100,0.1]))
        area = self.axes.get_area(graph=low, x_range=[0,100], bounded_graph=high)
        self.gaussians = []
        x_axis = np.arange(0,100,0.1)
        self.gaussians = plot_gaussian(self.axes, self.gaussians, x_axis, 1.4, 7.5, 1.3)
        self.gaussians = plot_gaussian(self.axes, self.gaussians, x_axis, 6.8, 9.8, 1.3)
        self.gaussians = plot_gaussian(self.axes, self.gaussians, x_axis, 0.4, 17, 4)
        self.gaussians = plot_gaussian(self.axes, self.gaussians, x_axis, 0.25, 31, 8)
        self.gaussians = plot_gaussian(self.axes, self.gaussians, x_axis, 0.009, 38, 30)

        self.gaussians = VGroup(*self.gaussians)


        y_pysr10 = []
        y_pysr15 = []
        y_pysr30 = []
        for i in x_axis:
            y_pysr10.append(self.pysr_equation10(i))
            y_pysr15.append(self.pysr_equation15(i))
            y_pysr30.append(self.pysr_equation30(i))

        y_pysr10 = np.array(y_pysr10)
        y_pysr15 = np.array(y_pysr15)
        y_pysr30 = np.array(y_pysr30)

        y_pysr10[y_pysr10<1e-6] = 1e-6
        y_pysr15[y_pysr15<1e-6] = 1e-6
        y_pysr30[y_pysr30<1e-6] = 1e-6

        self.pysr_10 = self.axes.plot_line_graph(x_values=x_axis,y_values=y_pysr10,stroke_width=8,add_vertex_dots=False,line_color=YELLOW)
        self.pysr_15 = self.axes.plot_line_graph(x_values=x_axis,y_values=y_pysr15,stroke_width=8,add_vertex_dots=False,line_color=YELLOW)
        self.pysr_30 = self.axes.plot_line_graph(x_values=x_axis,y_values=y_pysr30,stroke_width=8,add_vertex_dots=False,line_color=YELLOW)


        self.model = MathTex(r"p(m_1) \propto \sum_i f_i\mathcal{N}(m_1;\mu_i,\sigma_i)",font_size=40).shift(3*RIGHT,2*UP)
        self.play(FadeIn(self.model),FadeIn(median), FadeIn(area),*[FadeIn(self.gaussians[i]) for i in range(len(self.gaussians))])
        self.wait(0.5)
        self.play(Uncreate(self.model),*[Uncreate(self.gaussians[i]) for i in range(len(self.gaussians))])
        self.wait(0.5)
        self.play(Create(self.pysr_10), Write(self.label1))
        self.wait(0.5)
        self.play(Transform(self.pysr_10,self.pysr_15), Transform(self.label1,self.label2))
        self.wait(0.5)
        self.play(Transform(self.pysr_10,self.pysr_30), Transform(self.label1,self.label3))
        self.wait(0.5)