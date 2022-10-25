from manim import *

class LinearNN(Scene):
    def construct(self):
        edges = []
        partitions = []
        c = 0
        layers = [2, 3, 3, 2]  # the number of neurons in each layer

        for i in layers:
            partitions.append(list(range(c + 1, c + i + 1)))
            c += i
        for i, v in enumerate(layers[1:]):
                last = sum(layers[:i+1])
                for j in range(v):
                    for k in range(last - layers[i], last):
                        edges.append((k + 1, j + last + 1))

        vertices = np.arange(1, sum(layers) + 1)

        graph = Graph(
            vertices,
            edges,
            layout='partite',
            partitions=partitions,
            layout_scale=3,
            vertex_config={'radius': 0.20},
        )
        graph.z_index = -1
        graph.color = GRAY_C
        AnimationList = []
        self.play(Create(graph))
        for key in graph.edges:
            if partitions[0][0] in key:
                AnimationList.append(ShowPassingFlash(graph.edges[key].copy().set_color(WHITE),run_time=2,
                time_width=1))
        self.play(*AnimationList)

class LabeledModifiedGraph(Scene):
    def construct(self):
        vertices = [1, 2, 3, 4, 5, 6, 7, 8]
        edges = []
        for i in vertices:
            for j in vertices:
                if i < j:
                    edges.append((i, j))
        g = Graph(vertices, edges, layout="circular", layout_scale=3,
                  vertex_config={'radius': 0.20})
        g.color = GRAY_C
        print(g.edges[(1, 2)])
        animationList = []
        for i in vertices:
            animationList.append(Write(g.vertices[i]))
        self.play(AnimationGroup(*animationList,lag_ratio=0.1))
        animationList = []
        for i in vertices:
            for j in vertices:
                if i < j:
                    animationList.append(GrowFromPoint(g.edges[(i, j)], g.edges[(i, j)].start))
        self.play(*animationList)
        animationList = []
        for i in vertices:
            for key in g.edges:
                if i in key:
                    animationList.append(ShowPassingFlash(g.edges[key].copy().set_color(WHITE),run_time=2,
                    time_width=1))
        self.play(*animationList)