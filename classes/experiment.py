import easygui
import os
import pickle
import time

import pygame as pg

from classes import Light, LightSource, FlatMirror, SphericalMirror


class Experiment:

    def __init__(self, light = None, mirrors = [], light_source = None, light_destination = None):
        """
            Конструктор класса Эксперимент. Содержит все его параметры: зеркала, источник света,
                цель луча света, сам луч света. 
            Параметры:
                light (Light): луч света. По умолчанию None
                mirrors (List[Mirror]): список всех зеркал эксперимента. По умолчанию []
                light_source (LightSource): источник света. По умолчанию None
                light_destination (LightDestination): цель света. По умолчанию None
        """

        self.light = light
        self.mirrors = mirrors
        self.light_source = light_source
        self.light_destination = light_destination
        self.settings_mode = False # Режим настроек и изменения параметров
        self.advancing = False # Режим запущенного эксперимента (движения луча света)

    def turn_settings(self):
        """
            Переключает режим настроек.
        """

        self.settings_mode = not self.settings_mode

    def start(self):
        """
            Начало эксперимента, создание света.
        """

        self.light = Light(self.light_source)
        self.resume()

    def run(self, window):
        """
            Запуск программы.
        """

        self.running = True # Режим работы программы, завершается, если это значение = False
        self.curr_time = time.time()
        self.global_mirror_poses = [] # Позиции всех зеркал эксперимента в пространстве
        self.highlighted = None # Для режима настроек: выделенное зеркало
        self.is_highlighted = False # Флаг выделенного зеркала
        self.ready = False # Можно ли запустить эксперимент

        while self.running:

            if self.settings_mode: 
                self.settings_mode(window) # Режим настроек
            else:
                self.exp_mode(window) # Основной режим программы

    def exp_mode(self, window):
        """
            Основной режим программы. Здесь расположено меню загрузки, сохранения,
                а также запускается сам эксперимент.
        """

        screen = window.screen
        drawspace = window.drawspace

        has_event = False

        if not self.advancing: # Если эксперимент не запущен, следить за использованием кнопок

            for event in pg.event.get():

                has_event = True

                if event.type == pg.QUIT:
                    self.running = False
                    break

                drawspace.draw_mirrors()
                drawspace.draw_light_source()
                drawspace.draw_light_destination()

                if self.light_source is not None and self.light_destination is not None:
                    self.ready = True

                drawspace.draw_buttons(window.exp_mode_buttons, True)
                if not self.ready:
                    window.start_button.is_up = False
                    screen.blit(window.start_button.down_surface, window.start_button.pos)

                pg.display.flip()

                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    
                    mouse_x, mouse_y = event.pos

                    for button in window.exp_mode_buttons:
                        button_x, button_y = button.pos
                        this_button_width, this_button_height = button.size
                        if mouse_x >= button_x and mouse_x <= button_x + this_button_width and \
                                mouse_y >= button_y and mouse_y <= button_y + this_button_height:

                            if button.is_up:
                                screen.blit(button.down_surface, button.pos)
                                pg.display.flip()
                                button.is_up = False

                                button.action() 

        # Если событий не было, но есть свет, продолжить выполнение эксперимента
        if not has_event and self.light is not None:

            if not window.quit_button.is_up:
                screen.blit(window.quit_button.up_surface, window.quit_button.pos)
                window.quit_button.is_up = True

            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    self.pause()
                    break

                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    window.turn_buttons(event, window.exp_mode_buttons)

            if self.advancing:

                for button in [b for b in window.exp_mode_buttons if b is not window.quit_button]:
                    if button.is_up:
                        window.screen.blit(button.down_surface, button.pos)
                        pg.display.flip()
                        button.is_up = False
                self.running = self.run_exp(window) # Запуск самого эксперимента

    def settings_mode(self, window):
        """
            Режим настроек. Сюда включается режим рисования новой конфигурации
                зеркал и всех остальных параметров эксперимента.
        """

        drawspace = window.drawspace

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            drawspace.update_buttons(window.settings_mode_buttons)

            if len(self.mirrors) == 0:

                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:

                    button_pressed = window.turn_buttons(event, window.settings_mode_buttons)
                    if not button_pressed:
                        self.draw_mode(window, event.pos, drawspace) # Режим рисования

            else: # Изменение параметров

                if self.light_source is not None:
                    drawspace.update_buttons(window.with_source_buttons)
                    drawspace.draw_everything(window.with_source_buttons, self.is_highlighted)
                else:
                    drawspace.update_buttons(window.no_source_buttons)
                    drawspace.draw_everything(window.no_source_buttons, self.is_highlighted)

                self.is_highlighted = False
                self.highlighted = None

                if event.type == pg.MOUSEBUTTONDOWN or event.type == pg.MOUSEMOTION:

                    mouse_x, mouse_y = event.pos
                    
                    button_pressed = False
                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                        if self.light_source is not None:
                            button_pressed = window.turn_buttons(event, window.with_source_buttons)
                        else:
                            button_pressed = window.turn_buttons(event, window.no_source_buttons)

                    if not button_pressed:

                        new_mirror = None

                        for mirror in self.mirrors:

                            if isinstance(mirror, FlatMirror):
                                
                                outer_poly = mirror.get_outer_polygon()

                                # Если навели мышкой на какое-то из зеркал
                                if drawspace.is_point_in_polygon(event.pos, outer_poly): 
                                    self.is_highlighted = True
                                    self.highlighted = mirror
                                    # Если нажали левой кнопкой, открыть окно параметров
                                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                                        window.edit_mirror(event.type == pg.MOUSEBUTTONDOWN, mirror)
                                    # Если нажали правой кнопкой, открыть окно изменения типа зеркала
                                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                                        new_mirror = window.edit_mirror_type(mirror)
                                        if self.light_source is not None and self.light_source.mirror is mirror:
                                            self.light_source.mirror = new_mirror

                            elif isinstance(mirror, SphericalMirror):
                                
                                rounding_polygon = mirror.rounding_polygon

                                if drawspace.is_point_in_polygon(event.pos, rounding_polygon):
                                    self.is_highlighted = True
                                    self.highlighted = mirror
                                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                                        window.edit_mirror(event.type == pg.MOUSEBUTTONDOWN, mirror)
                                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                                        new_mirror = window.edit_mirror_type(mirror)
                                        if self.light_source is not None and self.light_source.mirror is mirror:
                                            self.light_source.mirror = new_mirror

                        if new_mirror is not None:
                            self.mirrors[self.mirrors.index(self.highlighted)] = new_mirror
        
                        # Если нажали на пустое пространство, создать здесь цель луча
                        if not self.is_highlighted and event.type == pg.MOUSEBUTTONDOWN:

                            window.edit_destination(event.pos)

    def add_light_source(self, mirror):
        """
            Создать источник света на заданном зеркале mirror.
        """

        self.light_source = LightSource(mirror)

    def draw_mode(self, window, start_pos, drawspace):
        """
            Режим рисования. 
            Параметры:
                window (Window): окно
                start_pos (float, float): точка, откуда рисуется последнее зеркало
                drawspace (DrawSpace): рисовальщик
        """

        draw_mode = True
        self.global_mirror_poses.append(start_pos)

        while draw_mode:

            while time.time() - self.curr_time < 0.02:
                pass

            self.curr_time = time.time()

            for event in pg.event.get():

                if event.type == pg.QUIT:
                    draw_mode = False
                    self.running = False
                    break

                # Рисовать зеркала, пока строится многоугольник. Остановиться, когда замкнули
                draw_mode = drawspace.draw_settling_mirrors(draw_mode, self.global_mirror_poses, event, window.settings_mode_buttons)

        # По умолчанию конфигурация формируется из плоских зеркал
        for prev_pos, next_pos in zip(self.global_mirror_poses, self.global_mirror_poses[1:] + [self.global_mirror_poses[0]]):
            self.mirrors.append(FlatMirror(prev_pos, next_pos))
        self.global_mirror_poses = []

        # Повернуть все зеркала внутрь фигуры
        drawspace.turn_mirrors_to_inside(self.mirrors)

    def run_exp(self, window):
        """
            Запущенный эксперимент. При достижении лучом света цели, выскакивает окно с успехом 
                и завершает программу. Если по истечении длительного времени цель не достигнута,
                программа завершается с ошибкой.
        """

        drawspace = window.drawspace

        drawspace.draw_light()

        while time.time() - self.light.last_tick < 0.01:
            pass

        self.light.advance()

        if self.light_destination.is_achieved(self.light):
            easygui.msgbox(msg = "Успех! Свет достиг требуемой зоны. Завершаем программу.", title = "Успех!")
            return False
        if self.light.momentum > 10000:
            easygui.msgbox(msg = "Ошибка: Свет движется слишком долго. Завершаем программу.", title = "Ошибка")
            return False
        mirror = self.light.is_clashed(self.mirrors, drawspace)
        if mirror is not None:
            dir_vec = mirror.reflect_light(self.light)
            self.light.reflection_points.append(self.light.current_point)
            self.light.direction_vec = dir_vec
        return True

    def pause(self):
        """
            Приостановка эксперимента.
        """
        self.advancing = False

    def resume(self):
        """
            Возобновление эксперимента.
        """

        self.advancing = True

    def save(self, file_path, save_name):
        """
            Режим сохранения. Запускает окно для сохранения конфигурации. Все файлы именуются расширением .exp.
            Параметры:
                file_path (str): путь к директории, где будут сохраняться эксперименты
                save_name (str): имя эксперимента для сохранения
        """
        if file_path is None or save_name is None:
            return

        experiment_config = {
            "light" : self.light,
            "mirrors" : self.mirrors,
            "light_source" : self.light_source,
            "light_destination" : self.light_destination
        }

        # Используется пакет pickle
        with open(os.path.join(file_path, save_name), 'wb') as save_file:
            pickle.dump(experiment_config, save_file)

    def load(self, file_path, load_name):
        """
            Режим загрузки. Запускает окно для загрузки конфигурации. Все файлы именуются расширением .exp.
            Параметры:
                file_path (str): путь к директории, где хранятся эксперименты
                save_name (str): имя эксперимента для загрузки
            Возвращает:
                experiment_config (dict): конфигурация эксперимента из файла
        """
        if file_path is None or load_name is None:
            return None

        with open(os.path.join(file_path, load_name), 'rb') as load_file:
            experiment_config = pickle.load(load_file)

        del self.light
        del self.mirrors
        del self.light_source
        del self.light_destination

        self.light = experiment_config["light"]
        self.mirrors = experiment_config["mirrors"]
        self.light_source = experiment_config["light_source"]
        self.light_destination = experiment_config["light_destination"]

        return experiment_config