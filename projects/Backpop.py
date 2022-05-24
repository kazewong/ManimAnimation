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
        for i in np.linspace(0,1,3):
            color_local = color.interpolate_color(color.RED,color.BLUE,i)
            binary = Binary(radius = 0.2,center = np.array([0,i,0]),rate=0.5,trail_length=0).set_color(color_local)
            self.add(binary)

        self.wait(1)
        

class Binary(VGroup):
    def __init__(self,radius=0.2,center: np.array=np.array([0,0,0]),rate = 0.1, period = 1,trail_length = 0,final_center = None):
        super().__init__()
        self.center = center
        self.dot1 = Dot3D()
        self.dot2 = Dot3D()
        self.orbit = Circle(radius=radius).rotate(PI/8,axis=LEFT).move_to(center)
        self.dot1_dt = 0.
        self.dot2_dt = 0.5
        self.path1 = VMobject()
        self.path2 = VMobject()

        def dot1_updater(mob, dt):
            self.orbit.move_to(self.center)
            self.dot1_dt += dt * rate
            self.dot1_dt = self.dot1_dt % period
            mob.move_to(self.orbit.point_from_proportion(self.dot1_dt))

        def dot2_updater(mob, dt):
            self.dot2_dt += dt * rate
            self.dot2_dt = self.dot2_dt % period
            mob.move_to(self.orbit.point_from_proportion(self.dot2_dt))

        def path1_updater(path):
            previous_path = path.copy()
            previous_path.add_points_as_corners([self.dot1.get_center()])
            previous_path.points = previous_path.points[-trail_length:]
            path.become(previous_path)

        def path2_updater(path):
            previous_path = path.copy()
            previous_path.add_points_as_corners([self.dot2.get_center()])
            previous_path.points = previous_path.points[-trail_length:]
            path.become(previous_path)

        self.dot1.move_to(self.orbit.point_from_proportion(self.dot1_dt))
        self.dot2.move_to(self.orbit.point_from_proportion(self.dot2_dt))
        self.path1.set_points_as_corners([self.dot1.get_center(), self.dot1.get_center()])
        self.path2.set_points_as_corners([self.dot2.get_center(), self.dot2.get_center()])
        self.dot1.add_updater(dot1_updater)
        self.dot2.add_updater(dot2_updater)
        self.path1.add_updater(path1_updater)
        self.path2.add_updater(path2_updater)

        self.add(self.dot1,self.dot2,self.path1,self.path2)
        
class BinaryToRemnent(VGroup):
    def __init__(self):
        self.binary_start = Binary(radius=0.2,center=np.array([0,0,0]),rate=0.1,period=1,trail_length=0)
        self.binary_end = Binary(radius=0.2,center=np.array([2,0,0]),rate=0.1,period=1,trail_length=0)

    @override_animation(Create)
    def _create(self,**kwargs):
        return AnimationGroup(Create(self.binary_start),Create(self.binary_end),lag_ratio=1)

