from os import abort
from turtle import circle
from manim import *
from gwcoords import *

alpha = 0
sin_delta = np.sin(3*np.pi/2) 
cos_iota = np.cos(np.pi/4)
psi = 0

class GWSkyAngle(ThreeDScene):
    def construct(self):
        self.skySphere = SkySphere()
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)



        self.play(Create(self.skySphere))
        L, west, wx, wy, k = get_orientation_vector(alpha, sin_delta, cos_iota, psi, full_output=True)

        self.dot = Dot(L*3)
        self.line = Line(ORIGIN,self.dot.get_center())
        self.path = VGroup()
        self.path.add(Line(self.dot.get_center(), self.dot.get_center()))
        self.zaxis = Line(ORIGIN, k*3, color=RED)
        self.xaxis = Line(ORIGIN, wx*3, color=GREEN)
        self.yaxis = Line(ORIGIN, wy*3, color=BLUE)
        self.zlabel = Tex("k").next_to(self.zaxis.get_end())
        self.xlabel = Tex("wx").next_to(self.xaxis.get_end())
        self.ylabel = Tex("wy").next_to(self.yaxis.get_end())
        self.Llabel = Tex("L").next_to(self.dot.get_center())

        self.add_fixed_orientation_mobjects(self.dot)
        self.add_fixed_orientation_mobjects(self.zlabel)
        self.add_fixed_orientation_mobjects(self.xlabel)
        self.add_fixed_orientation_mobjects(self.ylabel)
        self.add_fixed_orientation_mobjects(self.Llabel)

        def get_curve():
            last_line = self.path[-1]
            new_line = Line(last_line.get_end(),self.dot.get_center(), color=YELLOW_D)
            self.path.add(new_line)
            return self.path

        self.play(Create(self.xaxis), Create(self.yaxis), Create(self.zaxis), Create(self.zlabel), Create(self.xlabel), Create(self.ylabel),Create(self.Llabel),Create(self.dot),Create(self.line),run_time=1)
        self.add(always_redraw(get_curve))
        # self.play(Rotate(self.dot,angle=2*PI,axis=np.array([0,0,1]),about_point=ORIGIN,rate_func=linear),run_time=3)
        self.play(Rotate(self.dot,angle=2*PI,axis=np.array([0,0,1]),about_point=ORIGIN,rate_func=linear),
                Rotate(self.line,angle=2*PI,axis=np.array([0,0,1]),about_point=ORIGIN,rate_func=linear),
                Rotate(self.Llabel,angle=2*PI,axis=np.array([0,0,1]),about_point=ORIGIN,rate_func=linear),run_time=3)
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