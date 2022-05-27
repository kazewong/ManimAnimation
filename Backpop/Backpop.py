from cmath import isnan
from nturl2path import pathname2url
from telnetlib import DO
from turtle import circle
from manim import *

class OrbitingBinary(ThreeDScene):
    def construct(self):

        def powerLaw(x):
            output = -2*x+10
            return output
        self.distribution = Distribution(powerLaw)
        self.binaryProcess = BinaryToRemnent()
        self.add(self.distribution)
        # self.play(Create(self.distribution))
        # self.play(Create(self.binaryProcess))

        # for i in np.linspace(0,1,1):
        #     color_local = color.interpolate_color(color.RED,color.BLUE,i)
        #     binary = Binary(radius = 0.2,trail_length=10).set_color(color_local)
        #     self.add(binary)
        # self.play(Rotate(binary),run_time=3)
        

class Binary(VGroup):
    def __init__(self,radius=0.2,center: np.array=np.array([0,0,0]),trail_length = 0,final_center = None):
        super().__init__()
        self.center = center
        self.trail_length = trail_length
        self.dot1 = Dot3D().move_to(center)
        self.dot2 = Dot3D().move_to(center)
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

        
class BinaryToRemnent(VGroup):
    def __init__(self):
        super().__init__()
        self.binary_start = Binary(radius=0.2,center=np.array([0,0,0]),trail_length=0)
        self.binary_end = Binary(radius=0.2,center=np.array([2,0,0]),trail_length=0)
        self.arrow = Arrow(self.binary_start.get_center(),self.binary_end.get_center(),buff=0.1)

    @override_animation(Create)
    def _create(self,**kwargs):
        return AnimationGroup(Create(self.binary_start), Rotate(self.binary_start), GrowArrow(self.arrow), Create(self.binary_end),lag_ratio=1)


class Distribution(VGroup):
    def __init__(self, function):
        super().__init__()
        self.axes = Axes(x_range=[0,5], y_range=[0,10,10],axis_config={"include_tip": False})
        y_label = self.axes.get_y_axis_label(r"p(m_{1})", edge=2*LEFT, direction=2*LEFT)
        x_label = self.axes.get_x_axis_label(r"m_{1}", edge=DOWN, direction=DOWN,buff=10)
        grid_labels = VGroup(x_label, y_label)
        axis = np.linspace(0.1,5,100)
        self.graph = self.axes.plot_line_graph(x_values=axis,y_values=function(axis),line_color=RED,add_vertex_dots=False, stroke_width=4,)
        self.add(self.axes,self.graph, grid_labels)

    @override_animation(Create)
    def _create(self,**kwargs):
        return AnimationGroup(Create(self.axes),Create(self.graph),lag_ratio=1)