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



class OribitingBinary(ThreeDScene):
    def construct(self):
        
        axes = ThreeDAxes()
        self.setup()
        self.orbitAround()
        
        

    def setup(self):
        self.orbit = Circle(radius=2).rotate(PI/8,axis=LEFT)
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)

    def orbitAround(self):
        self.t_offset1 = 0.5
        self.t_offset2 = 0.

        def dot1_updater(mob, dt):
            self.t_offset1 += dt * 0.1
            self.t_offset1 = self.t_offset1 % 1
            mob.move_to(self.orbit.point_from_proportion(self.t_offset1))

        def dot2_updater(mob, dt):
            self.t_offset2 += dt * 0.1
            self.t_offset2 = self.t_offset2 % 1
            mob.move_to(self.orbit.point_from_proportion(self.t_offset2))

        def path1_updater(path):
            previous_path = path.copy()
            previous_path.add_points_as_corners([dot1.get_center()])
            previous_path.points = previous_path.points[-50:]
            path.become(previous_path)

        def path2_updater(path):
            previous_path = path.copy()
            previous_path.add_points_as_corners([dot2.get_center()])
            previous_path.points = previous_path.points[-50:]
            path.become(previous_path)

        dot1 = Dot3D()
        dot1.move_to(self.orbit.point_from_proportion(self.t_offset1))
        dot1.add_updater(dot1_updater)
        dot2 = Dot3D()
        dot2.move_to(self.orbit.point_from_proportion(self.t_offset2))
        dot2.add_updater(dot2_updater)

        path1 = VMobject()
        path1.set_points_as_corners([dot1.get_center(), dot1.get_center()])
        path1.add_updater(path1_updater)

        path2 = VMobject()
        path2.set_points_as_corners([dot2.get_center(), dot2.get_center()])
        path2.add_updater(path2_updater)

        self.add(dot1)
        self.add(dot2) 
        self.add(path1)
        self.add(path2)
        self.wait(10)