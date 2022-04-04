import math
import time

from classes.mirror import FlatMirror, SphericalMirror

def length(p1, p2): # Вспомогательная функция для подсчета длины отрезка между двумя точками

    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


class Light:

    def __init__(self, light_source = None):
        """
            Конструктор класса Light (луч света). 
            Параметры:
                light_source (LightSource): источник света, из которого идет луч (по умолчанию None)
        """

        self.source = light_source
        self.direction_vec = self.source.get_direction_vec() # Направление выхода света из источника
        self.current_point = self.source.get_absolute_pos() # Исходное положение луча света
        self.reflection_points = [self.current_point] # Точки преломления света (образуют ломаную)
        self.momentum = 0.0 # Момент света, отсчет от 0
        self.velocity = self.source.velocity # Скорость распространения света
        self.last_tick = time.time() # Движение во времени

    def advance(self):
        """
            Продвинуть луч света во времени.
        """

        tick_diff = time.time() - self.last_tick # Разность во времени
        self.momentum += tick_diff * 0.01 
        self.last_tick = time.time()

        # Сдвиг луча в сторону направления движения
        self.current_point = (self.current_point[0] + self.velocity * tick_diff * self.direction_vec[0], 
                                self.current_point[1] + self.velocity * tick_diff * self.direction_vec[1])

    def is_clashed(self, mirrors, drawspace):
        """
            Коснулся ли луч какого-то зеркала?
            Возращает:
                mirror (Mirror), которого коснулся; иначе None
        """

        for mirror in mirrors:
            if isinstance(mirror, FlatMirror):
                if drawspace.is_point_in_polygon(self.current_point, mirror.get_outer_polygon()):
                    return mirror
            elif isinstance(mirror, SphericalMirror):
                if drawspace.is_point_in_polygon(self.current_point, mirror.rounding_polygon):
                    if mirror.mirror_type == "convex":
                        if length(mirror.center, self.current_point) >= mirror.curv_radius:
                            return mirror
                    elif mirror.mirror_type == "concave":
                        if length(mirror.center, self.current_point) <= mirror.curv_radius:
                            return mirror

        return None


class LightSource:

    def __init__(self, mirror = None, local_pos = 0.5, light_direction = 90, velocity = 100.0):
        """
            Конструктор класса LightSource.
            Параметры:
                mirror (Mirror): зеркало, к которому крепится источник. По умолчанию None
                local_pos (float): значение от 0 до 1, означающее относительное положение на зеркале 
                    источника от левого края. По умолчанию 0.5
                light_direction (float): значение от 0 до 180, означающее угол выхода света относительно
                    правого края. По умолчанию 90
                velocity (float): скорость распространения света. По умолчанию 100.0
        """
        self.mirror = mirror
        self.local_pos = local_pos
        self.light_direction = light_direction
        self.velocity = velocity

    def get_absolute_pos(self):
        """
            Возвращает точку местоположения источника в пространстве.
        """

        mirror = self.mirror

        if isinstance(mirror, FlatMirror):
            left_corner = self.mirror.left_corner
            right_corner = self.mirror.right_corner

            x1, y1 = left_corner
            x2, y2 = right_corner

            pvecx, pvecy = x1 - x2, y1 - y2
            pvecx, pvecy = pvecx, pvecy
            mirror_len = math.sqrt(pvecx ** 2 + pvecy ** 2)
            pvecx, pvecy = pvecx / math.sqrt(pvecx ** 2 + pvecy ** 2), pvecy / math.sqrt(pvecx ** 2 + pvecy ** 2)

            x = x1 - pvecx * mirror_len * self.local_pos
            y = y1 - pvecy * mirror_len * self.local_pos

            return (x, y)
        elif isinstance(mirror, SphericalMirror):

            start_angle, stop_angle = mirror.start_angle, mirror.stop_angle

            local_pos = self.local_pos

            if mirror.mirror_type == "concave":
                local_pos = 1.0 - local_pos
            light_angle = start_angle + (stop_angle - start_angle) * local_pos
            light_angle = -light_angle

            center = mirror.center
            radius = mirror.curv_radius 
            p = (center[0] + radius, center[1])
            opvec = (p[0] - center[0], p[1] - center[1])

            light_pos_vec_x = opvec[0] * math.cos(light_angle) - opvec[1] * math.sin(light_angle)
            light_pos_vec_y = opvec[0] * math.sin(light_angle) + opvec[1] * math.cos(light_angle)

            light_pos = (light_pos_vec_x + center[0], light_pos_vec_y + center[1])

            return light_pos

    def get_direction_vec(self):
        """
            Возвращает вектор направления света. 
        """

        rad = self.light_direction * math.pi / 180

        left_corner = self.mirror.left_corner
        right_corner = self.mirror.right_corner

        x1, y1 = left_corner
        x2, y2 = right_corner

        pvecx, pvecy = x1 - x2, y1 - y2
        pvecx, pvecy = pvecx, pvecy
        pvecx, pvecy = pvecx / math.sqrt(pvecx ** 2 + pvecy ** 2), pvecy / math.sqrt(pvecx ** 2 + pvecy ** 2)

        dirvecx = pvecx * math.cos(rad) - pvecy * math.sin(rad)
        dirvecy = pvecx * math.sin(rad) + pvecy * math.cos(rad)

        return (dirvecx, dirvecy)


class LightDestination:

    def __init__(self, pos = (0, 0), radius = 1.0):
        """
            Конструктор цели луча света.
            Параметры:
                pos (float, float): местоположение в пространстве. По умолчанию (0, 0)
                radius (float): радиус цели. По умолчанию 1.0
        """
        self.pos = pos
        self.radius = radius

    def is_achieved(self, light):
        """
            Возвращает True, если луч света (заданный как параметр light) коснулся цели. Иначе возвращает False 
        """

        light_pos = light.current_point

        if (light_pos[0] - self.pos[0]) ** 2 + (light_pos[1] - self.pos[1]) ** 2 < self.radius ** 2:
            return True

        return False