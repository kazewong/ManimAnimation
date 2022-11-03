from manim import *

class Bayes2HBayes(Scene):
    def construct(self):
        eq1 = MathTex(r"p(\theta|D) = \frac{p_l(D|h(\theta))\pi(\theta)}{p_e(D)}")
        eq2 = MathTex(r"p(\lambda|D) = \frac{p_l(D|h(\theta))p_{\rm pop}(\theta|\lambda)\pi(\lambda)}{p_e(D)}")
        self.play(Write(eq1))
        self.wait(0.5)
        self.play(ReplacementTransform(eq1,eq2))