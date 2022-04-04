import math
import pygame as pg
from pygame import Color


class Mirror:

    def __init__(self, left_corner = (0, 0), right_corner = (1, 1)):
        """
        Конструктор класса Mirror.
    
        Параметры:
            left_corner (float, float): Координаты левого края зеркала (по умолчанию (0, 0)) 
            right_corner (float, float): Координаты правого края зеркала (по умолчанию (1, 1))
        """

        self.left_corner = left_corner
        self.right_corner = right_corner

        self.mirror_color = Color("grey75")
        self.wood_color = Color("burlywood4")

        # Точка по центру отрезка, соединяющего оба края зеркала
        self.central_point = (float(left_corner[0] + right_corner[0]) / 2, float(left_corner[1] + right_corner[1]) / 2)

    def get_dir_norm_vecs(self, left_corner = None, right_corner = None):
        """
        Возвращает единичный направляющий вектор прямой от левого к правому краю и единичнй нормальный вектор к ней же. 

        Параметры:
            left_corner (float, float): Координаты левого края зеркала (по умолчанию self.left_corner) 
            right_corner (float, float): Координаты правого края зеркала (по умолчанию self.right_corner)
        Возвращает:
            (float, float), (float, float): направляющий и нормальный вектора
        """

        if left_corner is None:
            left_corner = self.left_corner
        if right_corner is None:
            right_corner = self.right_corner

        x1, y1 = left_corner
        x2, y2 = right_corner

        # Направляющий вектор
        pvecx, pvecy = x1 - x2, y1 - y2
        pvecx, pvecy = pvecx, pvecy
        pvecx, pvecy = pvecx / math.sqrt(pvecx ** 2 + pvecy ** 2), pvecy / math.sqrt(pvecx ** 2 + pvecy ** 2)

        # Нормальный вектор
        nvecx, nvecy = y2 - y1, x1 - x2
        nvecx, nvecy = -nvecx, -nvecy
        nvecx, nvecy = nvecx / math.sqrt(nvecx ** 2 + nvecy ** 2), nvecy / math.sqrt(nvecx ** 2 + nvecy ** 2)

        return (pvecx, pvecy), (nvecx, nvecy)

    def get_flat_length(self):
        """
        Возвращает длину отрезка, образованного левым и правым краями зеркала. 

        Возвращает:
            float: длина отрезка
        """

        m = math.sqrt((self.left_corner[0] - self.right_corner[0]) ** 2 + (self.left_corner[1] - self.right_corner[1]) ** 2)
        return m


class FlatMirror(Mirror):

    def __init__(self, left_corner = (0, 0), right_corner = (1, 1)):
        """
            Конструктор класса FlatMirror (плоское зеркало), подкласс Mirror.
            Параметры:
                left_corner (float, float): Координаты левого края зеркала (по умолчанию (0, 0)) 
                right_corner (float, float): Координаты правого края зеркала (по умолчанию (1, 1))
        """

        super().__init__(left_corner, right_corner)

        self.left_mirror_end, self.right_mirror_end, self.left_base_end, self.right_base_end = self.calculate_points(left_corner, right_corner)

    def calculate_points(self, left_corner = None, right_corner = None):
        """
            Вычисление разных краёв зеркала. 
            Параметры:
                left_corner (float, float): Координаты левого края зеркала (по умолчанию self.left_corner) 
                right_corner (float, float): Координаты правого края зеркала (по умолчанию self.right_corner)
            Возвращает:
                (float, float), (float, float), (float, float), (float, float): 
                    точка левого заднего края зеркала, 
                    точка правого заднего края зеркала,
                    точка левого заднего края корпуса зеркала,
                    точка правого заднего края корпуса зеркала
        """

        if left_corner is None:
            left_corner = self.left_corner
        if right_corner is None:
            right_corner = self.right_corner

        x1, y1 = left_corner
        x2, y2 = right_corner

        self.pvec, self.nvec = self.get_dir_norm_vecs(left_corner, right_corner)
        pvecx, pvecy = self.pvec
        nvecx, nvecy = self.nvec

        base_width = 10 # Толщина всего корпуса зеркала
        mirrow_width = 5 # Толщина самого зеркала

        x3, y3 = x2 + base_width * (nvecx + pvecx), y2 + base_width * (nvecy + pvecy)
        x4, y4 = x1 + base_width * (nvecx - pvecx), y1 + base_width * (nvecy - pvecy)

        x5, y5 = x2 + mirrow_width * (nvecx + pvecx), y2 + mirrow_width * (nvecy + pvecy)
        x6, y6 = x1 + mirrow_width * (nvecx - pvecx), y1 + mirrow_width * (nvecy - pvecy)

        return (x6, y6), (x5, y5), (x4, y4), (x3, y3)

    def recalculate_points(self):
        """
            Пересчёт всех частей зеркала при изменении параметров.
        """

        self.left_mirror_end, self.right_mirror_end, self.left_base_end, self.right_base_end = self.calculate_points(
                self.left_corner, self.right_corner)

        self.central_point = (float(self.left_corner[0] + self.right_corner[0]) / 2, float(self.left_corner[1] + self.right_corner[1]) / 2)

    def reflect_light(self, light):
        """
            Отразить свет.
            Параметры:
                light (Light): луч света, созданный в эксперименте
            Возвращает:
                new_dir (float, float): направление отраженного луча
        """

        x1, y1 = self.left_corner
        x2, y2 = self.right_corner

        nvecx, nvecy = self.get_dir_norm_vecs()[1]

        curr_dir = light.direction_vec

        dot = curr_dir[0] * nvecx + curr_dir[1] * nvecy
        diff_vec = (2 * dot * nvecx, 2 * dot * nvecy)

        new_dir = (curr_dir[0] - diff_vec[0], curr_dir[1] - diff_vec[1])

        return new_dir

    def get_outer_polygon(self):
        """
            Возвращает четырехугольник, образующий корпус.
        """

        left_corner = self.left_corner
        right_corner = self.right_corner
        left_base_end = self.left_base_end
        right_base_end = self.right_base_end

        return [left_corner, right_corner, right_base_end, left_base_end]

    def get_inner_polygon(self):
        """
            Возвращает четырехугольник, образующий само зеркало.
        """

        left_corner = self.left_corner
        right_corner = self.right_corner
        left_mirror_end = self.left_mirror_end
        right_mirror_end = self.right_mirror_end

        return [left_corner, right_corner, right_mirror_end, left_mirror_end]


class SphericalMirror(Mirror):

    def __init__(self, left_corner = (0, 0), right_corner = (1, 1), mirror_type = "convex", curv_radius = 150.0):
        """
            Конструктор сферического зеркала. 
            Параметры:
                left_corner (float, float): Координаты левого края зеркала (по умолчанию (0, 0)) 
                right_corner (float, float): Координаты правого края зеркала (по умолчанию (1, 1))
                mirror_type (["convex", "concave"]): Тип зеркала. "convex" -> выпуклое, "concave" -> вогнутое. По умолчанию "convex"
                curv_radius (float): Радиус кривизны зеркала. По умолчанию 150.0
        """
        super().__init__(left_corner, right_corner)

        self.mirror_type = mirror_type 
        self.curv_radius = curv_radius

        # Расстояние от центральной точки на отрезке до центра окружности кривизны
        self.radius_dist = math.sqrt(
            self.curv_radius ** 2 - 
            (self.central_point[0] - self.left_corner[0]) ** 2 - 
            (self.central_point[1] - self.left_corner[1]) ** 2
        )

        self.spherical_rect = self.build_spherical_rect()

        self.rounding_polygon = self.build_rounding_polygon()

        self.start_angle, self.stop_angle = self.get_angles()

    def recalculate_points(self):
        """
            Пересчёт всех частей зеркала при изменении параметров.
        """

        self.central_point = (float(self.left_corner[0] + self.right_corner[0]) / 2, float(self.left_corner[1] + self.right_corner[1]) / 2)
        self.radius_dist = math.sqrt(
            self.curv_radius ** 2 - 
            (self.central_point[0] - self.left_corner[0]) ** 2 - 
            (self.central_point[1] - self.left_corner[1]) ** 2
        )
        self.spherical_rect = self.build_spherical_rect()

        self.rounding_polygon = self.build_rounding_polygon()

        self.start_angle, self.stop_angle = self.get_angles()

    def build_rounding_polygon(self):
        """
            Построение описывающего зеркало прямоугольника.
        """

        x1, y1 = self.left_corner
        x2, y2 = self.right_corner

        nvecx, nvecy = self.get_dir_norm_vecs()[1]

        if self.mirror_type == "convex":
            x3, y3 = x2 + nvecx * (self.curv_radius - self.radius_dist), y2 + nvecy * (self.curv_radius - self.radius_dist)
            x4, y4 = x1 + nvecx * (self.curv_radius - self.radius_dist), y1 + nvecy * (self.curv_radius - self.radius_dist)
            return [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        else:
            x3, y3 = x2 + nvecx * (self.radius_dist - self.curv_radius), y2 + nvecy * (self.radius_dist - self.curv_radius)
            x4, y4 = x1 + nvecx * (self.radius_dist - self.curv_radius), y1 + nvecy * (self.radius_dist - self.curv_radius)
            return [(x1, y1), (x4, y4), (x3, y3), (x2, y2)]   

    def build_spherical_rect(self):
        """
            Построение описывающего окружность кривизны прямоугольника.
        """

        x1, y1 = self.left_corner
        x2, y2 = self.right_corner

        (pvec, pvecy), (nvecx, nvecy) = self.get_dir_norm_vecs()
        nvecx, nvecy = -nvecx, -nvecy

        if self.mirror_type == "convex":
            self.center = (self.central_point[0] + self.radius_dist * nvecx, self.central_point[1] + self.radius_dist * nvecy)
        else:
            self.center = (self.central_point[0] - self.radius_dist * nvecx, self.central_point[1] - self.radius_dist * nvecy)
        left_top = (self.center[0] - self.curv_radius, self.center[1] - self.curv_radius)

        return pg.Rect(left_top, (self.curv_radius * 2, self.curv_radius * 2))

    def get_angles(self):
        """
            Углы левого и правого краев зеркала по окружности кривизны.
        """

        x1, y1 = self.left_corner
        x2, y2 = self.right_corner

        p = (self.center[0] + self.curv_radius, self.center[1])

        opvec = (p[0] - self.center[0], p[1] - self.center[1])
        orcvec = (x2 - self.center[0], y2 - self.center[1])
        olcvec = (x1 - self.center[0], y1 - self.center[1])

        stop_cos = float(opvec[0] * orcvec[0] + opvec[1] * orcvec[1]) / (self.curv_radius * self.curv_radius)
        stop_angle = math.acos(stop_cos)

        start_cos = float(opvec[0] * olcvec[0] + opvec[1] * olcvec[1]) / (self.curv_radius * self.curv_radius)
        start_angle = math.acos(start_cos)

        if self.mirror_type == "concave":
            start_angle, stop_angle = stop_angle, start_angle
            if y2 > self.center[1]:
                start_angle = math.pi * 2 - start_angle
            if y1 > self.center[1]:
                stop_angle = math.pi * 2 - stop_angle
        else:
            if y1 > self.center[1]:
                start_angle = math.pi * 2 - start_angle
            if y2 > self.center[1]:
                stop_angle = math.pi * 2 - stop_angle

        return start_angle, stop_angle

    def reflect_light(self, light):
        """
            Отразить свет.
            Параметры:
                light (Light): луч света, созданный в эксперименте
            Возвращает:
                new_dir (float, float): направление отраженного луча
        """

        x1, y1 = self.left_corner
        x2, y2 = self.right_corner

        x0, y0 = self.center

        xn, yn = light.current_point

        nvecx, nvecy = xn - x0, yn - y0
        nvecx, nvecy = nvecx / math.sqrt(nvecx ** 2 + nvecy ** 2), nvecy / math.sqrt(nvecx ** 2 + nvecy ** 2)
        if self.mirror_type == "concave":
            nvecx, nvecy = -nvecx, -nvecy 

        curr_dir = light.direction_vec

        dot = curr_dir[0] * nvecx + curr_dir[1] * nvecy
        diff_vec = (2 * dot * nvecx, 2 * dot * nvecy)

        new_dir = (curr_dir[0] - diff_vec[0], curr_dir[1] - diff_vec[1])

        return new_dir
