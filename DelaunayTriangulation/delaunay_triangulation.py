from manim import *
import numpy as np

["radii", "centers", "keys", "values", "vertices"]


def read_data(filename: str):
    data = np.load(filename)
    simplices = dict()
    vertices = data["vertices"]
    centroid = np.mean(vertices[:, :3], axis=1)
    for i in range(len(data["keys"])):
        simplices[data["keys"][i]] = [
            data["values"][:, i],
            data["radii"][i],
            data["centers"][:, i] - centroid,
        ]
    return simplices, vertices.T - centroid


def plot_simplex_2d(simplex: dict[int, np.array], vertices: list[float]):
    x, y = [], []
    for vertex_id in [0, 1, 2]:
        x.append(vertices[simplex[vertex_id] - 1][0])
        y.append(vertices[simplex[vertex_id] - 1][1])
    return x, y


simplices = []
vertices = []
for i in range(3, 20):
    _simplices, _vertices = read_data("./data/tree_{}.npz".format(str(i).zfill(4)))
    simplices.append(_simplices)
    vertices.append(_vertices)


class Simplex(VGroup):
    def __init__(
        self,
        vertices,
        dot_color: list[str] | str = WHITE,
        line_color: list[str] | str = WHITE,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.dot_group = VGroup()
        for vertex in vertices:
            if isinstance(dot_color, list):
                color = dot_color.pop(0)
            else:
                color = dot_color
            self.dot_group.add(
                Dot(np.array([vertex[0], vertex[1], 0]) * 2, color=color)
            )
        self.line_group = VGroup()
        for i in range(3):
            if isinstance(line_color, list):
                color = line_color.pop(0)
            else:
                color = line_color
            self.line_group.add(
                Line(
                    self.dot_group[i].get_center(),
                    self.dot_group[(i + 1) % 3].get_center(),
                    color=color,
                )
            )
        self.add(self.dot_group, self.line_group)

    @override_animation(Create)
    def _create(self, dot=True, line=True, **kwargs):
        output = []
        if dot:
            output.append(AnimationGroup(*[Create(dot) for dot in self.dot_group]))
        if line:
            output.append(AnimationGroup(*[Create(line) for line in self.line_group]))
        return AnimationGroup(*output, lag_ratio=0.85)

    @override_animation(Uncreate)
    def _uncreate(self, dot=True, line=True, **kwargs):
        output = []
        if dot:
            output.append(AnimationGroup(*[Uncreate(dot) for dot in self.dot_group]))
        if line:
            output.append(AnimationGroup(*[Uncreate(line) for line in self.line_group]))
        return AnimationGroup(*output, lag_ratio=0.85)

    @override_animation(Indicate)
    def _indicate(self, **kwargs):
        return Indicate(self.dot_group, **kwargs)


class TwoInsertion(Scene):
    def construct(self):
        simplex = Simplex(vertices[0][:3])
        circumcircle = Circle.from_three_points(
            *[np.array([vertices[0][i][0], vertices[0][i][1], 0]) * 2 for i in range(3)]
        ).set_color(WHITE)

        new_vertex = Dot(
            np.array([vertices[0][6][0], vertices[0][6][1], 0]) * 2, z_index=100
        )

        new_simplex_group = VGroup()
        simplex_with_vertex = np.array([[7, 1, 2], [7, 1, 3], [7, 2, 3]])
        color_list = [RED, GREEN, BLUE]
        for i in range(3):
            new_simplex_group.add(
                Simplex(
                    vertices[0][simplex_with_vertex[i] - 1],
                    dot_color=color_list[i],
                    line_color=color_list[i],
                )
            )

        self.play(Create(simplex))
        self.play(Create(new_vertex))
        self.play(Create(circumcircle))
        animation_group = AnimationGroup(
            *[
                Indicate(simplex, scale_factor=1, color=RED),
                Indicate(circumcircle, scale_factor=1, color=RED),
            ]
        )
        self.play(animation_group)
        self.play(Uncreate(circumcircle))
        animation_group = AnimationGroup(
            *[Create(simplex, dot=False) for simplex in new_simplex_group]
        )
        self.play(animation_group)

        new_vertex = Dot(
            np.array([vertices[0][7][0], vertices[0][7][1], 0]) * 2, z_index=100
        )
        new_simplex_group = VGroup()
        simplex_with_vertex = np.array([[8, 7, 1], [8, 7, 2], [8, 1, 2]])
        color_list = [RED, GREEN, BLUE]
        for i in range(3):
            new_simplex_group.add(
                Simplex(
                    vertices[0][simplex_with_vertex[i] - 1],
                    dot_color=color_list[i],
                    line_color=color_list[i],
                )
            )
        animation_group = AnimationGroup(
            *[Create(simplex) for simplex in new_simplex_group]
        )
        circumcircle = Circle.from_three_points(
            *[
                np.array([vertices[0][i][0], vertices[0][i][1], 0]) * 2
                for i in [6, 0, 1]
            ]
        ).set_color(WHITE)

        self.play(Create(new_vertex))
        self.play(Create(circumcircle))
        self.play(Indicate(circumcircle, scale_factor=1, color=RED))
        self.play(Uncreate(circumcircle))
        self.play(animation_group)


class ConstructDelanuayTriangulation(Scene):
    def construct(self):
        # Insert vertices
        for vertex in vertices:
            self.play(Create(Dot(np.array([vertex[0], vertex[1], 0]) * 2)))

        # for simplex in simplices.values():
        #     x, y = plot_simplex_2d(simplex[0], vertices)
        #     self.play(Create(Polygon(*[np.array([x[i], y[i], 0]) for i in range(3)])))
        # self.wait(2)


class DelaunayToVoronoi(Scene):
    def construct(self):
        pass
