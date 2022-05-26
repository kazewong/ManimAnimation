from nturl2path import pathname2url
from telnetlib import DO
from turtle import circle
from manim import *
class DefaultTemplate(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        circle.set_fill(PINK, opacity=0.5)  # set color and transparency

        square = Square()  # create a square
        square.flip(RIGHT)  # flip horizontally
        square.rotate(-3 * TAU / 8)  # rotate a certain amount

        self.play(Create(square))  # animate the creation of the square
        self.play(Transform(square, circle))  # interpolate the square into the circle
        self.play(FadeOut(square))  # fade out animation

class OrbitingBinary(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        # self.play(Create(BinaryToRemnent(),lag_ratio=3,run_time=3))
        dot = Dot()
        for i in np.linspace(0,1,1):
            color_local = color.interpolate_color(color.RED,color.BLUE,i)
            binary = Binary(radius = 0.2,trail_length=10).set_color(color_local)
            self.add(binary)
        self.play(Rotate(binary),run_time=3)
        

class Binary(VGroup):
    def __init__(self,radius=0.2,center: np.array=np.array([0,0,0]),trail_length = 0,final_center = None):
        super().__init__()
        self.center = center
        self.trail_length = trail_length
        self.dot1 = Dot3D()
        self.dot2 = Dot3D()
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
        dot1_rotate = Rotate(self.dot1,angle=6*PI,about_point=ORIGIN,rate_func=linear,)
        dot2_rotate = Rotate(self.dot2,angle=6*PI,about_point=ORIGIN,rate_func=linear,)
        return AnimationGroup(dot1_rotate,dot2_rotate)




        
class BinaryToRemnent(VGroup):
    def __init__(self):
        self.binary_start = Binary(radius=0.2,center=np.array([0,0,0]),rate=0.1,period=1,trail_length=0)
        self.binary_end = Binary(radius=0.2,center=np.array([2,0,0]),rate=0.1,period=1,trail_length=0)

    @override_animation(Create)
    def _create(self,**kwargs):
        return AnimationGroup(Create(self.binary_start),Create(self.binary_end),lag_ratio=1)

