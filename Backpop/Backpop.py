from cProfile import run
from cmath import isnan
from nturl2path import pathname2url
from telnetlib import DO
from turtle import circle
from manim import *

class OrbitingBinary(ThreeDScene):
    def construct(self):

        # Prepare objects
        def powerLaw(x):
            output = -2*x+10
            return output
        self.distribution = Distribution(powerLaw)
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
        self.play(Transform(self.distribution, self.distribution.copy().rotate(PI/2).scale(0.25).shift(3*LEFT)))

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
        for i in range(n_binary-1,-1,-1):
            AnimationList.append(FadeOut(arrowList[i],shift=RIGHT,scale=0))
            AnimationList.append(Transform(binaryList[i],remnentList[i]))
        self.play(AnimationGroup(*[GrowArrow(arrowList[i]) for i in range(n_binary-1,-1,-1)],lag_ratio=0.2))
        self.play(AnimationGroup(*AnimationList,lag_ratio=0.2))



        

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
    def __init__(self, function):
        super().__init__()
        self.axes = Axes(x_range=[0,5], y_range=[0,10,10],axis_config={"include_tip": False})
        y_label = self.axes.get_y_axis_label(r"p(m_{1})", edge=LEFT, direction=LEFT).rotate(PI/2).shift(0.5*LEFT)
        x_label = self.axes.get_x_axis_label(r"m_{1}", edge=DOWN, direction=DOWN,buff=10)
        self.grid_labels = VGroup(x_label, y_label)
        axis = np.linspace(0.1,5,100)
        self.graph = self.axes.plot_line_graph(x_values=axis,y_values=function(axis),line_color=RED,add_vertex_dots=False, stroke_width=4,)
        self.add(self.axes,self.graph, self.grid_labels)

    @override_animation(Create)
    def _create(self,**kwargs):
        return AnimationGroup(Create(self.axes),Create(self.graph),Create(self.grid_labels),lag_ratio=0.5)