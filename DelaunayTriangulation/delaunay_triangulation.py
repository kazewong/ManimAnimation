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

simplices = []
vertices = []
_simplices, _vertices = read_data('./data/tree.npz')
for i in range(3, 20):
    _simplices, _vertices = read_data('./data/tree_{}.npz'.format(str(i).zfill(4)))
    simplices.append(_simplices)
    vertices.append(_vertices)

class Simplex(VGroup):
    def __init__(self, vertices, **kwargs):
        super().__init__(**kwargs)
        self.dot_group = VGroup()
        for vertex in vertices:
            self.dot_group.add(Dot(np.array([vertex[0], vertex[1], 0])*2))
        self.line_group = VGroup()
        for i in range(3):
            self.line_group.add(Line(self.dot_group[i].get_center(), self.dot_group[(i+1)%3].get_center()))
        self.add(self.dot_group, self.line_group)
        
    @override_animation(Create)
    def _create(self,**kwargs):
        anigroup1 = AnimationGroup(*[Create(dot) for dot in self.dot_group])
        anigroup2 = AnimationGroup(*[Create(line) for line in self.line_group])
        return AnimationGroup(anigroup1, anigroup2, lag_ratio=0.85)

class InitialConstruction(Scene):
    def construct(self):
        simplex = Simplex(vertices[0][:3])
        self.play(Create(simplex))

class OneInsertion(Scene):
    def construct(self):
        
        initial_simplex = Simplex(vertices[1][:3])
        self.add(initial_simplex)

        new_vertex = Dot(np.array([vertices[1][6][0], vertices[1][6][1], 0]))
        line_group = VGroup()
        
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