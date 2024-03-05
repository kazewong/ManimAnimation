from manim import *
import numpy as np

['radii', 'centers', 'keys', 'values', 'vertices']

def read_data(filename: str):
    data = np.load(filename)
    simplices = dict()
    vertices = data['vertices']
    centroid = np.mean(vertices[:,:3], axis=1)
    for i in range(len(data['keys'])):
        simplices[data['keys'][i]] = [data['values'][:, i], data['radii'][i], data['centers'][:,i]-centroid]
    return simplices, vertices.T - centroid

def plot_simplex_2d(simplex: dict[int, np.array], vertices: list[float]):
    x, y = [], []
    for vertex_id in [0,1,2]:
        x.append(vertices[simplex[vertex_id]-1][0])
        y.append(vertices[simplex[vertex_id]-1][1])
    return x, y

simplices, vertices = read_data('/home/kaze/Work/Presentation/ManimAnimation/DelaunayTriangulation/tree.npz')

class InitialConstruction(Scene):
    def construct(self):
        dot_group = VGroup()
        for vertex in vertices[:3]:
            dot_group.add(Dot(np.array([vertex[0], vertex[1], 0])*2))
        animation_group = AnimationGroup(*[Create(Dot(np.array([vertex[0], vertex[1], 0])*2)) for vertex in vertices[:3]])
        self.play(animation_group)
        line_group = VGroup()
        for i in range(3):
            line_group.add(Line(dot_group[i].get_center(), dot_group[(i+1)%3].get_center()))
        animation_group = AnimationGroup(*[Create(line) for line in line_group])
        self.play(animation_group)
class ConstructDelanuayTriangulation(Scene):
    def construct(self):
        #Insert vertices
        for vertex in vertices:
            self.play(Create(Dot(np.array([vertex[0], vertex[1], 0])*2)))

        # for simplex in simplices.values():
        #     x, y = plot_simplex_2d(simplex[0], vertices)
        #     self.play(Create(Polygon(*[np.array([x[i], y[i], 0]) for i in range(3)])))
        # self.wait(2)
            
class DelaunayToVoronoi(Scene):
    def construct(self):
        pass