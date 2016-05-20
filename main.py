from __future__ import division
import glfw
import copy
from OpenGL.GL import *
import numpy

window_width = 400
window_height = 400
vertices = []
edges = []
line = []
cutted_line = []
debug = False
to_redraw = True
to_draw_line = False
to_slice = False


def key_callback(window, key, scancode, action, mods):
    global vertices, to_redraw, debug, to_draw_line, line, edges, cutted_line, to_slice
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, 1)
            return
        if key == glfw.KEY_S:
            cutted_line = []
            to_slice = not to_slice  # )))
            to_redraw = True
        if key == glfw.KEY_L:
            to_draw_line = not to_draw_line
        if key == glfw.KEY_C:
            vertices = []
            edges = []
            line = []
            cutted_line = []
            to_draw_line = False
            to_redraw = True


def resize_callback(window, width, height):
    pass


def mouse_button_callback(window, button, action, mods):
    global vertices, to_redraw, window_height, window_width
    if action == glfw.PRESS:
        to_redraw = True
        coordinates_of_click = glfw.get_cursor_pos(window)

        # get rounded coordinates for pixel matrix
        coordinates = ((coordinates_of_click[0] - window_width / 2),
                       (window_height - coordinates_of_click[1] - window_height / 2))
        # print(coordinates)
        if to_draw_line:
            length = len(line)
            if length == 0:
                line.append(coordinates)
            elif length == 1:
                line.append(coordinates)
            else:
                line.pop(0)
                line.append(coordinates)
        else:
            if len(vertices) == 0 or (vertices[-1][0] != coordinates[0] and vertices[-1][1] != coordinates[1]):
                vertices.append(coordinates)


# func with creating edges
def compute_edges():
    global edges, vertices
    edges = []
    for i in range(len(vertices) - 1):
        edges.append([vertices[i], vertices[i + 1]])
    if len(edges) > 1: edges.append([vertices[len(vertices) - 1], vertices[0]])


def get_norm_direction(line1, line2):
    z = line1[0] * line2[1] - line1[1] * line2[0]
    if z == 0:
        return 0
    elif z > 0:
        return 1
    else:
        return -1


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return False

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def in_polygon(x, y, xp, yp):
    c = 0
    for i in range(len(xp)):
        if (((yp[i] <= y and y < yp[i - 1]) or (yp[i - 1] <= y and y < yp[i])) and \
                    (x > (xp[i - 1] - xp[i]) * (y - yp[i]) / (yp[i - 1] - yp[i]) + xp[i])): c = 1 - c
    return c


def slice():
    global line, debug, cutted_line, to_slice
    cutted_line = line[:]

    for edge in edges:
        result = line_intersection(edge, line)

        if result and min(edge[0][0], edge[1][0]) < result[0] < max(edge[0][0], edge[1][0]) \
                and min(edge[0][1], edge[1][1]) < result[1] < max(edge[0][1], edge[1][1]) \
                and min(line[0][0], line[1][0]) < result[0] < max(line[0][0], line[1][0]) \
                and min(line[0][1], line[1][1]) < result[1] < max(line[0][1], line[1][1]):
            print("intersected ")
            print(result)
            cutted_line.insert(len(cutted_line) - 1, result)


def draw():
    global to_redraw, cutted_line, line

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if to_redraw:
        compute_edges()
        if to_slice and len(line) == 2:
            slice()
        to_redraw = False

    for edge in edges:
        glBegin(GL_LINES)
        glColor3f(1, 1, 1)
        glVertex2f(edge[0][0] / (window_width / 2), edge[0][1] / (window_width / 2))
        glColor3f(1, 1, 1)
        glVertex2f(edge[1][0] / (window_width / 2), edge[1][1] / (window_width / 2))
        glEnd()

    if to_slice:
        cutted_line = sorted(cutted_line, key=lambda x: x[0])

        #creating list of x and y vertices
        x_vertices, y_vertices = [], []
        for v in vertices:
            x_vertices.append(v[0])
            y_vertices.append(v[1])

        if to_draw_line and in_polygon(cutted_line[0][0], cutted_line[0][1], x_vertices, y_vertices) == 1:
            a = 1
            print("first point inside polygon\n")
        else: a = 0

        for i in range(1, len(cutted_line)):
            glBegin(GL_LINES)
            glColor3f((i + a) % 2, 0, 0)
            glVertex2f(cutted_line[i - 1][0] / (window_width / 2), cutted_line[i - 1][1] / (window_width / 2))
            glColor3f((i + a) % 2, 0, 0)
            glVertex2f(cutted_line[i][0] / (window_width / 2), cutted_line[i][1] / (window_width / 2))
            glEnd()
    elif to_draw_line and len(line) == 2:
        glBegin(GL_LINES)
        glColor3f(1, 0, 0)
        glVertex2f(line[0][0] / (window_width / 2), line[0][1] / (window_width / 2))
        glColor3f(1, 0, 0)
        glVertex2f(line[1][0] / (window_width / 2), line[1][1] / (window_width / 2))
        glEnd()


def main():
    global vertices, window_height, window_width, to_redraw

    if not glfw.init():
        return

    window = glfw.create_window(400, 400, "Lab4", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_framebuffer_size_callback(window, resize_callback)

    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(0, 0, 0, 0)

    while not glfw.window_should_close(window):
        # print(vertices)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        draw()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == '__main__':
    main()
