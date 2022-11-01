from typing import Dict, Union, List
from pyglet.gl import *
import numpy as np

# data
anchor_points: Union[np.ndarray, None] = None
entity: Dict[str, Union[np.ndarray, None]] = {"points": None, "faces": None}
num_of_segments = 0
current_rotation_axis: Union[np.ndarray, None] = None


def load_anchor_points(path: str) -> None:
    if not path.endswith('.obj'):
        raise Exception('only .obj files can be parsed')

    global anchor_points, num_of_segments, current_rotation_axis

    with open(path, 'r') as file:
        for line in file:
            if line.startswith('#') or line.startswith('g'):
                continue

            point = line.split()
            if anchor_points is None:
                anchor_points = np.array([[float(point[1]), float(point[2]), float(point[3])]])
            else:
                anchor_points = np.append(anchor_points,
                                          np.array([[float(point[1]), float(point[2]), float(point[3])]]), axis=0)
        # scale values of points to fit camera view
        anchor_points /= np.max(np.max(anchor_points, axis=0) - np.min(anchor_points, axis=0))
        num_of_segments = len(anchor_points) - 3
        current_rotation_axis = np.reshape(anchor_points[1] / np.linalg.norm(anchor_points[1]), (1, 3))


def load_object(path: str) -> None:
    if not path.endswith('.obj'):
        raise Exception('only .obj files can be parsed')

    global entity

    with open(path, 'r') as file:
        for line in file:
            if line.startswith('#') or line.startswith('g'):
                continue

            if line.startswith('v'):
                point = line.split()
                if entity["points"] is None:
                    entity["points"] = np.array([[float(point[1]), float(point[2]), float(point[3])]])
                else:
                    entity["points"] = np.append(entity["points"],
                                                 np.array([[float(point[1]), float(point[2]), float(point[3])]]),
                                                 axis=0)
            elif line.startswith('f'):
                face = line.split()
                if entity["faces"] is None:
                    entity["faces"] = np.array([[int(face[1]), int(face[2]), int(face[3])]])
                else:
                    entity["faces"] = np.append(entity["faces"],
                                                np.array([[int(face[1]), int(face[2]), int(face[3])]]), axis=0)


# b-splain
t_values = np.linspace(0, 1, num=10)
B = np.array([[-1., 3., -3., 1.],
              [3., -6., 3., 0.],
              [-3., 0., 3., 0.],
              [1., 4., 1., 0.]]) / 6.
current_segment_idx = 0
current_t_idx = 0


def do_loop(*args):
    global current_t_idx, current_segment_idx
    new_t = current_t_idx + 1
    if new_t >= len(t_values):
        new_t = 0
        new_segment = current_segment_idx + 1
        if new_segment >= num_of_segments:
            new_segment = 0
        current_segment_idx = new_segment
    current_t_idx = new_t


def get_point(t, R) -> np.array:
    t_array = np.array([[t ** 3, t ** 2, t, 1.]])
    return np.dot(np.dot(t_array, B), R)


def get_dt(t, R) -> np.array:
    t_array = np.array([[3 * t ** 2, 2 * t, 1, 0]])
    return np.dot(np.dot(t_array, B), R)


def get_dt_dt(t, R) -> np.array:
    t_array = np.array([[6 * t, 2, 0, 0]])
    return np.dot(np.dot(t_array, B), R)


def calculate_segement_tangents(points: np.array) -> np.array:
    tangents = None
    for t in t_values:
        if tangents is None:
            tangents = get_dt(t, points)
        else:
            tangents = np.append(tangents, get_dt(t, points), axis=0)
    return tangents


def calculate_segment(points: np.array) -> np.array:
    segment = None
    for t in t_values:
        if segment is None:
            segment = get_point(t, points)
        else:
            segment = np.append(segment, get_point(t, points), axis=0)
    return segment


def calculate_rotation_matrix() -> np.ndarray:
    current_params = t_values[current_t_idx], anchor_points[current_segment_idx:current_segment_idx + 4]
    w = get_dt(*current_params)
    dt_dt = get_dt_dt(*current_params)
    u = np.cross(w, dt_dt)
    v = np.cross(w, u)
    return np.linalg.inv(np.vstack((w, u, v)).transpose() * 100) / 100

def get_angle(s, e) -> float:
    return np.rad2deg(np.arccos(np.dot(s, e.transpose()) / (np.linalg.norm(s) * np.linalg.norm(e))))

def calculate_rotation_axis(e) -> List:
    return list(np.cross(current_rotation_axis, e)[0])


def calculate_position() -> List:
    return list(get_point(t_values[current_t_idx], anchor_points[current_segment_idx:current_segment_idx + 4])[0])


# view settings
width: int = 1500
height: int = 800
window = pyglet.window.Window(width, height)


camera: Dict[str, List[float]] = {"position": [0, 0, 0], "target": [0, 0, 0], "up": [0, 0, 0]}


def adjust_camera() -> None:
    global camera
    target = np.mean(anchor_points, axis=0)
    position = target + np.array([2., 2., 5.])
    up = np.array([0., 0., 1.])

    camera["position"] = list(position)
    camera["target"] = list(target)
    camera["up"] = list(up)


def draw_path() -> None:
    glPointSize(5)
    glBegin(GL_POINTS)
    glColor3f(1., 0.5, 0.31)
    for point in anchor_points:
        glVertex3f(point[0], point[1], point[2])
    glEnd()

    glLoadIdentity()
    glPointSize(1)
    glColor3f(1., 1., 1.)
    glBegin(GL_LINE_STRIP)
    for segement_idx in range(num_of_segments):
        segment = calculate_segment(anchor_points[segement_idx:segement_idx + 4])
        segement_tangents = segment + calculate_segement_tangents(anchor_points[segement_idx:segement_idx + 4]) * 0.5
        for point, tang in zip(segment, segement_tangents):
            glVertex3f(point[0], point[1], point[2])
            glVertex3f(tang[0], tang[1], tang[2])
    glEnd()


def draw_object(rotation: np.ndarray = None) -> None:
    glPointSize(1)
    glColor3f(1., 0.5, 0.31)
    glScalef(0.1, 0.1, 0.1)
    glBegin(GL_TRIANGLES)
    for face in entity["faces"]:
        for number in face:
            idx = int(number) - 1
            point = [entity["points"][idx][0],
                     entity["points"][idx][1],
                     entity["points"][idx][2]]
            if rotation is not None:
                point = np.dot(np.array([point]), rotation)[0]
            glVertex3f(point[0],
                       point[1],
                       point[2])
    glEnd()


@window.event
def on_draw():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(10, float(width) / float(height), 0.1, 100.)
    gluLookAt(*camera["position"], *camera["target"], *(camera["up"]))

    glMatrixMode(GL_MODELVIEW)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    draw_path()

    glTranslatef(*calculate_position())

    """    
    ROTATION 1
    
    tangent = get_dt(t_values[current_t_idx], anchor_points[current_segment_idx:current_segment_idx + 4])
    roatation_axis = calculate_rotation_axis(tangent)
    angle = get_angle(current_rotation_axis, tangent)
    glRotatef(angle, *roatation_axis)
    draw_object()
    """

    """
    ROATATION 2
    
    """
    glScalef(100, 100,  100)
    dcm = calculate_rotation_matrix()
    print(dcm)
    draw_object(dcm)


if __name__ == '__main__':
    load_anchor_points('paths/path.obj')
    load_object('entities/cube.obj')
    adjust_camera()
    pyglet.clock.schedule(do_loop)
    pyglet.app.run()
