import math

import pygame as pg
from pygame import Color

from classes import FlatMirror, SphericalMirror

class DrawSpace:

    def __init__(
            self, 
            screen, 
            experiment, 
            exp_mode_buttons, 
            settings_mode_buttons
        ):
        """
            Конструктор рисовальщика. Отвечает за все геометрические вычисления и работу с рисованием в окне.
            Параметры: 
                screen (Surface): экран, на котором работает рисовальщик
                experiment (Experiment): текущий эксперимент
                exp_mode_buttons (List[Button]): кнопки основого режима программы
                settings_mode_buttons (List[Button]): кнопки режима настроек
        """

        self.experiment = experiment
        self.screen = screen

        self.exp_mode_buttons = exp_mode_buttons
        self.settings_mode_buttons = settings_mode_buttons
        
        # Цвета разных частей окна
        self.mirror_color = Color("grey75")
        self.wood_color = Color("burlywood4")
        self.light_color = Color("goldenrod1")
        self.dest_color = Color("cornflowerblue")
        self.caption_color = Color("black")
        self.light_caption_color = Color("goldenrod4")
        self.bg_color = Color("azure")

        self.screen.fill(self.bg_color)
        for button in self.exp_mode_buttons:
            self.screen.blit(button.up_surface, button.pos)

        pg.display.flip()

    def length(left, right):
        """
            Длина отрезка между двумя точками.
        """
        return math.sqrt((left[0] - right[0]) ** 2 + (left[1] - right[1]) ** 2)

    def draw_everything(self, buttons, is_highlighted = True):
        """
            "Нарисуй всё": отрисовка всех частей программы. 
            Параметры:
                buttons (List[Button]): рисуемые кнопки
                is_highlighted (bool): Рисовать ли отладочную информацию о конфигурации зеркал
        """

        self.screen.fill(self.bg_color)

        self.draw_buttons(buttons)
        self.draw_mirrors(show_corners = True)
        if is_highlighted:
            self.draw_highlights()
        self.draw_light_source(light_radius = 10, view_direction = True)
        self.draw_light_destination(show_pos = True)

        pg.display.flip()

    def draw_buttons(self, buttons, turn_up = False):
        """
            Рисование кнопок buttons и поднять их, если turn_up = True
        """

        for button in buttons:
            self.screen.blit(button.up_surface, button.pos)
            if turn_up:
                button.is_up = True

    def update_buttons(self, buttons):
        """
            Обновить текстуры кнопок buttons
        """
        for button in buttons:
            if not button.is_up:
                self.screen.blit(button.up_surface, button.pos)
                pg.display.flip()
                button.is_up = True

    def draw_mirrors(self, show_corners = False):
        """
            Рисование зеркал. Если show_corners = True, выделяет края
        """

        if show_corners:
            corner_point_radius = 12

        for mirror in self.experiment.mirrors:

            left_corner = mirror.left_corner
            right_corner = mirror.right_corner

            if isinstance(mirror, FlatMirror):
                
                left_mirror_end = mirror.left_mirror_end
                right_mirror_end = mirror.right_mirror_end
                left_base_end = mirror.left_base_end
                right_base_end = mirror.right_base_end

                pg.draw.polygon(self.screen, self.wood_color, [left_corner, right_corner, right_base_end, left_base_end])
                pg.draw.polygon(self.screen, self.mirror_color, [left_corner, right_corner, right_mirror_end, left_mirror_end])
                if show_corners:
                    pg.draw.circle(self.screen, self.wood_color, left_corner, corner_point_radius)

            if isinstance(mirror, SphericalMirror):

                arc_width = 5
                mirror_rect = mirror.spherical_rect

                pg.draw.arc(self.screen, self.mirror_color, mirror_rect, mirror.start_angle, mirror.stop_angle, width = arc_width)
                if show_corners:
                    pg.draw.circle(self.screen, self.wood_color, left_corner, corner_point_radius)

    def draw_highlights(self):
        """
            Рисование отладочной информации. Рисуется, если выделено какое-то зеркало.
        """

        mirror = self.experiment.highlighted

        left_corner = mirror.left_corner
        right_corner = mirror.right_corner

        font = pg.font.Font(None, 40)
        left_point_text = font.render("Left: " + str(left_corner), True, self.caption_color)
        right_point_text = font.render("Right: " + str(right_corner), True, self.caption_color)
        left_point_pos_x, left_point_pos_y = (left_corner[0] - 100, left_corner[1] - 50)
        right_point_pos_x, right_point_pos_y = (right_corner[0] - 100, right_corner[1] - 50)

        if left_point_pos_x < 0:
            left_point_pos_x = left_corner[0] + 100 
        if left_point_pos_y < 0:
            left_point_pos_y = left_corner[1] + 50

        if right_point_pos_x < 0:
            right_point_pos_x = right_corner[0] + 100 
        if right_point_pos_y < 0:
            right_point_pos_y = right_corner[1] + 50

        if left_point_pos_x > 1080-200:
            left_point_pos_x = left_corner[0] - 100 
        if left_point_pos_y > 720-200:
            left_point_pos_y = left_corner[1] - 50

        if right_point_pos_x > 1080-200:
            right_point_pos_x = right_corner[0] - 100
        if right_point_pos_y > 720-200:
            right_point_pos_y = right_corner[1] - 50

        left_point_pos = (left_point_pos_x, left_point_pos_y)
        right_point_pos = (right_point_pos_x, right_point_pos_y)

        self.screen.blit(left_point_text, left_point_pos)
        self.screen.blit(right_point_text, right_point_pos)

        if self.experiment.light_source is not None and self.experiment.light_source.mirror is mirror:
            light_point_text = font.render("Light source: " + str(self.experiment.light_source.get_absolute_pos()), True, self.light_caption_color)
            light_angle_text = font.render("Angle: " + str(self.experiment.light_source.light_direction), True, self.light_caption_color)
            apx, apy = self.experiment.light_source.get_absolute_pos()
            light_point_pos = (apx, apy + 50)
            light_angle_pos = (apx, apy + 75)
            self.screen.blit(light_point_text, light_point_pos)
            self.screen.blit(light_angle_text, light_angle_pos)
                
    
    def draw_light_source(self, light_radius = 4, view_direction = False):
        """
            Рисование источника света с радиусом в light_radius в отладочном режиме. 
                view_direction позволяет указать направление выходящего луча света. 
        """
        light_source = self.experiment.light_source
        if light_source is None:
            return

        lspos = light_source.get_absolute_pos()
        
        pg.draw.circle(self.screen, self.light_color, lspos, light_radius)
        if view_direction:
            dirvec = light_source.get_direction_vec()
            line_end = (dirvec[0] * 50 + lspos[0], dirvec[1] * 50 + lspos[1])
            pg.draw.line(self.screen, self.light_color, lspos, line_end, 5)

        pg.display.flip()

    def draw_light_destination(self, show_pos = False):
        """
            Рисование цели света. Если show_pos = True, показывает координаты и радиус цели.
        """

        light_destination = self.experiment.light_destination
        if light_destination is None:
            return

        ldpos = light_destination.pos 
        radius = light_destination.radius
        
        pg.draw.circle(self.screen, self.dest_color, ldpos, radius)

        if show_pos:

            font = pg.font.Font(None, 40)
            pos_point_text = font.render("Pos: " + str(ldpos), True, self.dest_color)
            radius_point_text = font.render("Radius: " + str(radius), True, self.dest_color)

        pg.display.flip()

    def draw_light(self):
        """
            Отрисовка луча света (его ломаной линии).
        """

        if self.experiment.light is None:
            return

        points = [self.experiment.light_source.get_absolute_pos()] + self.experiment.light.reflection_points

        for prev_point, next_point in zip(points, points[1:] + [self.experiment.light.current_point]):
            pg.draw.line(self.screen, self.light_color, prev_point, next_point, 5)

        pg.display.flip()


    def is_point_in_polygon(self, point, polygon):
        """
            Возвращает, входит ли данная точка point в многоугольник polygon.
        """

        is_inside = True
        xp, yp = point

        for (x1, y1), (x2, y2) in zip(polygon, polygon[1:] + [polygon[0]]):
            D = (x2 - x1) * (yp - y1) - (xp - x1) * (y2 - y1)

            if D < 0:
                is_inside = False
                break

        return is_inside

    def draw_settling_mirrors(self, draw_mode, global_mirror_poses, event, buttons):
        """
            Отрисовка зеркал в режиме рисования.
        """

        for prev_pos, next_pos in zip(global_mirror_poses, global_mirror_poses[1:]):
            pg.draw.line(self.screen, self.mirror_color, prev_pos, next_pos, width = 10)

        pg.display.flip()

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:

            self.settings_refill(global_mirror_poses, buttons)

            mouse_x, mouse_y = event.pos

            first_x, first_y = global_mirror_poses[0]
            if abs(first_x - mouse_x) < 20 and abs(first_y - mouse_y) < 20:
                pg.draw.line(self.screen, self.mirror_color, global_mirror_poses[0], global_mirror_poses[-1], width = 10)
                pg.display.flip()
                draw_mode = False
            else:
                if self.has_collision(global_mirror_poses[:-1], global_mirror_poses[-1], event.pos):
                    print("Collision Error")
                else:
                    global_mirror_poses.append(event.pos)

        if event.type == pg.MOUSEMOTION:

            self.settings_refill(global_mirror_poses, buttons)

            mouse_x, mouse_y = event.pos

            pg.draw.line(self.screen, self.mirror_color, global_mirror_poses[-1], event.pos, width = 10)
            pg.display.flip()

        return draw_mode

    def settings_refill(self, mirror_poses, buttons):
        """
            Обновление режима настроек.
        """
        self.screen.fill(self.bg_color)
        for button in buttons:
            self.screen.blit(button.up_surface, button.pos)
        for prev_pos, next_pos in zip(mirror_poses, mirror_poses[1:]):
            pg.draw.line(self.screen, self.mirror_color, prev_pos, next_pos, width = 10)
        self.draw_light_destination()
        pg.display.flip()

    def ccw(self, pos1, pos2, pos3):
        return (pos3[1] - pos1[1]) * (pos2[0] - pos1[0]) > (pos2[1] - pos1[1]) * (pos3[0] - pos1[0])

    def has_collision(self, mirror_poses, last_pos, curr_pos):
        """
            Возвращает True, если отрезок (last_pos, curr_pos) пересекает какое-то из зеркал в mirror_poses
        """

        for prev_pos, next_pos in zip(mirror_poses, mirror_poses[1:]):
            if self.ccw(prev_pos, last_pos, curr_pos) != self.ccw(next_pos, last_pos, curr_pos) and \
                    self.ccw(prev_pos, next_pos, last_pos) != self.ccw(prev_pos, next_pos, curr_pos):
                return True

        return False

    def turn_mirrors_to_inside(self, mirrors):
        """
            Поворот всех зеркал вовнутрь фигуры.
        """

        this_mirror = mirrors[0]

        _, nvec = this_mirror.get_dir_norm_vecs()
        central_point = this_mirror.central_point
        distant_point = (central_point[0] - nvec[0] * 5000, central_point[1] - nvec[1] * 5000)

        intersection_count = 0

        other_mirrors_poses = [m.left_corner for m in mirrors]
        for opos1, opos2 in zip(other_mirrors_poses[1:-1], other_mirrors_poses[2:]):
            if self.has_collision([opos1, opos2], central_point, distant_point):
                intersection_count += 1

        if intersection_count % 2 == 0:
            for mirror in mirrors:
                mirror.left_corner, mirror.right_corner = mirror.right_corner, mirror.left_corner
                mirror.recalculate_points()