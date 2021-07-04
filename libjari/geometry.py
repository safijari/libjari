from dataclasses import dataclass
import numpy as np
import cv2

@dataclass
class RectF:
    x: float
    y: float
    w: float
    h: float

    def pad(self, padding):
        self.x -= padding
        self.y -= padding
        self.h += padding * 2
        self.w += padding * 2

    def pad_asym(self, px, py):
        self.x -= px
        self.y -= py
        self.h += py * 2
        self.w += px * 2

    def resize(self, sx, sy):
        self.x *= sx
        self.y *= sy
        self.w *= sx
        self.h *= sy

    def resize_copy(self, sx, sy):
        out = self.copy()
        out.resize(sx, sy)
        return out

    def expand(self, sx, sy):
        self.x -= self.w * sx
        self.y -= self.h * sy
        self.w += 2 * self.w * sx
        self.h += 2 * self.h * sy

    def expand_copy(self, sx, sy):
        out = self.copy()
        out.expand(sx, sy)
        return out

    @property
    def x1(self):
        return self.x

    @property
    def y1(self):
        return self.y

    @property
    def x2(self):
        return self.x + self.w

    @property
    def y2(self):
        return self.y + self.h

    @x1.setter
    def x1(self, new_val):
        old_x2 = self.x2
        if new_val > old_x2:
            self.x = old_x2
            self.w = new_val - old_x2
        else:
            self.x = new_val
            self.w = old_x2 - new_val

    @x2.setter
    def x2(self, new_val):
        old_x1 = self.x1
        if new_val < old_x1:
            self.x = new_val
            self.w = old_x1 - new_val
        else:
            self.x = new_val
            self.w = new_val - old_x1

    @y1.setter
    def y1(self, new_val):
        old_y2 = self.y2
        if new_val > old_y2:
            self.y = old_y2
            self.h = new_val - old_y2
        else:
            self.y = new_val
            self.h = old_y2 - new_val

    @y2.setter
    def y2(self, new_val):
        old_y1 = self.y1
        if new_val < old_y1:
            self.y = new_val
            self.h = old_y1 - new_val
        else:
            self.y = new_val
            self.h = new_val - old_y1

    def intersect(self, other):
        return not (
            self.x > other.x + other.w
            or self.x + self.w < other.x
            or self.y > other.y + other.h
            or self.y + self.h < other.y
        )

    def horizontal_out_of_rect(self, other):
        return self.x < other.x or self.x > other.x + other.w or self.x + self.w > other.x + other.w

    def union_bound(self, other):
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.x + self.w, other.x + other.w) - x
        h = max(self.y + self.h, other.y + other.h) - y
        return RectF(x, y, w, h)

    def intersect_bound(self, other):
        tmp = self.__class__.from_dict(self.dictify())
        x, y, w, h = 0, 0, 0, 0

        if self & other:
            x = max(self.x, other.x)
            y = max(self.y, other.y)
            w = min(self.x + self.w, other.x + other.w) - x
            h = min(self.y + self.h, other.y + other.h) - y
        tmp.x = x
        tmp.y = y
        tmp.w = w
        tmp.h = h
        return tmp

    def intersection_area(self, other):
        return self.intersect_bound(other).area()

    def center_xy(self):
        return np.mean(np.array([[self.x1, self.y1], [self.x2, self.y2]]), axis=0)

    def contain_bound(self, other):
        return (
            other.x + other.w < self.x + self.w
            and other.x > self.x
            and other.y > self.y
            and other.y + other.h < self.y + self.h
        )

    def area(self):
        return self.w * self.h

    def validate_rect(self):
        if int(self.w) <= 0 or int(self.h) <= 0 or int(self.x) < 0 or int(self.y) < 0:
            return False
        else:
            return True

    @property
    def rect(self):
        return self

    @rect.setter
    def rect(self, _rectf):
        self.x = _rectf.x
        self.y = _rectf.y
        self.w = _rectf.w
        self.h = _rectf.h

    def bound_points(self, points):
        if len(points) == 0:
            raise Exception("empty points")
        min_x = points[0][0]
        max_x = points[0][0]
        min_y = points[0][1]
        max_y = points[0][1]
        for point in points[1:]:
            if min_x > point[0]:
                min_x = point[0]
            if max_x < point[0]:
                max_x = point[0]
            if min_y > point[1]:
                min_y = point[1]
            if max_y < point[1]:
                max_y = point[1]
        self.x = min_x
        self.y = min_y
        self.w = max_x - min_x
        self.h = max_y - min_y

    def __and__(self, other):
        return self.intersect(other)

    def __add__(self, other):
        return self.union_bound(other)

    def __mul__(self, other):
        return self.intersect_bound(other)

    def __eq__(self, other):
        are_equal = self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h
        return are_equal

    def crop_image(self, input_image, border=0):
        return self.crop_image_return_rect(input_image, border)[0]

    def crop_image_return_rect(self, im: np.ndarray, border=0):  # -> Tuple[np.ndarray, RectF]:
        b = border
        shp = im.shape
        d = shp[2] if len(shp) > 2 else None
        h, w = shp[0:2]
        rx1, ry1 = self.x, self.y
        rx2, ry2 = rx1 + self.w, ry1 + self.h
        y1 = int(max(ry1 - b, 0))
        y2 = int(min(ry2 + b, h))
        x1 = int(max(rx1 - b, 0))
        x2 = int(min(rx2 + b, w))
        crop = im[y1:y2, x1:x2, :] if d else im[y1:y2, x1:x2]
        return crop, RectF(x1, y1, x2 - x1, y2 - y1)

    def draw_on_image(self, im, color=(0, 255, 0), thickness=2):
        cv2.rectangle(
            im, (int(self.x1), int(self.y1)), (int(self.x2), int(self.y2)), color, thickness,
        )

    def copy(self):
        return self.__class__.from_dict(self.dictify())

    def is_empty(self):
        return self.x == 0 and self.y == 0 and self.w == 0 and self.h == 0

@dataclass
class Point2F:
    x: float
    y: float

    def __sub__(self, other):
        return Point2F(x=self.x - other.x, y=self.y - other.y)

    @property
    def square_mag(self):
        return self.x ** 2 + self.y ** 2

    @property
    def mag(self):
        return np.sqrt(self.square_mag)

@dataclass
class QuadF:
    p1: Point2F
    p2: Point2F
    p3: Point2F
    p4: Point2F

    @classmethod
    def from_rectf(cls, r):
        return cls(Point2F(x=r.x1, y=r.y1), Point2F(x=r.x2, y=r.y1), Point2F(x=r.x2, y=r.y2), Point2F(x=r.x1, y=r.y2),)

    @classmethod
    def from_coords(cls, x1, y1, x2, y2, x3, y3, x4, y4):
        return cls(Point2F(x=x1, y=y1), Point2F(x=x2, y=y2), Point2F(x=x3, y=y3), Point2F(x=x4, y=y4),)

    @property
    def points(self):
        return [self.p1, self.p2, self.p3, self.p4]

    def crop_image(self, im):
        """
        assumption is that p1 is "upper left" or "left most"
        and the rest of the points come in clockwise order when y is down
        """
        w = np.sqrt(max((self.p2 - self.p1).square_mag, (self.p4 - self.p3).square_mag))
        h = np.sqrt(max((self.p3 - self.p2).square_mag, (self.p1 - self.p4).square_mag))
        return project_image_using_warp_mat(im, warp_mat_from_verts(self.points, h, w, inv=True), h, w)

    def draw_on_image(self, im, color=(0, 255, 0), thickness=2):
        pts = self.points
        for p1, p2 in zip(pts, pts[1:] + [pts[0]]):
            cv2.line(im, (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), color, thickness)