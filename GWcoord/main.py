from os import abort
from turtle import circle
from manim import *
from gwcoords import *

class GWSkyAngle(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        self.skySphere = SkySphere()
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.play(Create(axes))

        self.play(Create(self.skySphere))
        L = get_orientation_vector(0, np.sin(np.pi/4), np.cos(np.pi/4),0,full_output=True)
        print(L)

        self.dot = Dot3D(L*3)
        self.line = Line(ORIGIN,self.dot.get_center())
        self.path = VGroup()
        self.path.add(Line(self.dot.get_center(), self.dot.get_center()))

        def get_curve():
            last_line = self.path[-1]
            new_line = Line(last_line.get_end(),self.dot.get_center(), color=YELLOW_D)
            self.path.add(new_line)
            return self.path

        self.add(always_redraw(get_curve))
        self.play(Rotate(self.dot,angle=2*PI,axis=np.array([0,0,1]),about_point=ORIGIN,rate_func=linear),Rotate(self.line,angle=2*PI,axis=np.array([0,0,1]),about_point=ORIGIN,rate_func=linear),run_time=3)
        self.wait(2)

class SkySphere(VGroup):
    def __init__(self,radius = 3):
        super().__init__()
        self.circle1 = Circle(radius=radius).rotate(PI/2,np.array([1,0,0]))
        self.circle2 = Circle(radius=radius).rotate(PI/2,np.array([0,1,0]))
        self.circle3 = Circle(radius=radius).rotate(PI/2,np.array([0,0,1]))
        self.add(self.circle1, self.circle2, self.circle3)

    @override_animation(Create)
    def _create(self,**kwargs):
        return AnimationGroup(Create(self.circle1),Create(self.circle2),Create(self.circle3))