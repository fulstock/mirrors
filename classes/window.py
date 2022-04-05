import pygame as pg
import easygui

import os
import time

from classes.button import Button
from classes.drawspace import DrawSpace
from classes.light import LightDestination
from classes.mirror import FlatMirror, SphericalMirror

class Window:

    def __init__(
            self, 
            experiment, 
            root_path = os.getcwd(), 
            saves_path = "saves", 
            logo = pg.image.load("logo.png"), 
            caption = "Зеркальный эксперимент",
            window_size = (1080, 720)
        ):
        """
            Конструктор окна.
        """

        self.root_path = root_path # Папка проекта
        self.saves_path = saves_path # Папка с сохранениями

        pg.init()
        pg.display.set_icon(logo)
        pg.display.set_caption(caption)
        self.screen = pg.display.set_mode(window_size)

        self.experiment = experiment

        self.setup_buttons() # Создать кнопки для всех режимов

        # Создать рисовальщика
        self.drawspace = DrawSpace(self.screen, self.experiment, self.exp_mode_buttons, self.settings_mode_buttons)

    def clear_main(self):
        """
            Обновить окно в основном режиме.
        """

        self.experiment.global_mirror_poses = []
        self.screen.fill(self.drawspace.bg_color)
        for button in self.exp_mode_buttons:
            self.screen.blit(button.up_surface, button.pos)
        pg.display.flip()

    def load_save(self):
        """
            Запуск окна загрузки эксперимента.
        """

        del self.experiment.mirrors
        self.experiment.mirrors = []

        exp_config = self.experiment.load(
            file_path = self.saves_path, 
            load_name = easygui.fileopenbox(
                msg = "Загрузить эксперимент",
                default = os.path.join(self.root_path, self.saves_path, "*.exp")
            )
        )

        if exp_config:
            self.clear_main()
            self.experiment.ready = True

    def boot_settings(self):
        """
            Запуск режима настроек.
        """
        self.screen.fill(self.drawspace.bg_color)
        self.drawspace.draw_mirrors()
        self.drawspace.draw_light_destination()
        for button in self.settings_mode_buttons:
            button.is_up = False
        last_tick = time.time()
        while time.time() - last_tick < 0.05:
            pass
        for button in self.settings_mode_buttons:
            button.is_up = True
            self.screen.blit(button.up_surface, button.pos)
        pg.display.flip()
        self.experiment.turn_settings()

    def deboot_settings(self):
        """
            Выключение режима настроек.
        """
        self.screen.fill(self.drawspace.bg_color)
        for button in self.exp_mode_buttons:
            button.is_up = False
        last_tick = time.time()
        while time.time() - last_tick < 0.05:
            pass
        for button in self.exp_mode_buttons:
            button.is_up = True
            self.screen.blit(button.up_surface, button.pos)
        pg.display.flip()
        self.experiment.turn_settings()

    def clear_field(self):
        """
            Очищение всего поля в режиме настроек.
        """
        self.global_mirror_poses = []
        del self.experiment.mirrors
        self.experiment.mirrors = []
        del self.experiment.light_source
        self.experiment.light_source = None
        del self.experiment.light_destination
        self.experiment.light_destination = None

        self.screen.fill(self.drawspace.bg_color)
        for button in self.settings_mode_buttons:
            self.screen.blit(button.up_surface, button.pos)
        pg.display.flip()

    def setup_buttons(self, margin = 30, button_width = 150, button_height = 50):
        """
            Создание всех кнопок.
        """

        self.quit_button = Button( pos = (margin, self.screen.get_height() - margin - button_height), 
                              size = (button_width, button_height),
                              text = "Выход",
                              font_size = 32,
                              action = lambda : pg.event.post(pg.event.Event(pg.QUIT)))
        self.save_button = Button( pos = (margin, margin), 
                              size = (button_width, button_height), 
                              text = "Сохранить", 
                              font_size = 32,
                              action = lambda : self.experiment.save(file_path = self.saves_path, 
                                    save_name = easygui.filesavebox(
                                        msg = "Сохранить эксперимент",
                                        default = os.path.join(self.root_path, self.saves_path, "*.exp") 
                            )))

        self.load_button = Button( pos = (margin, margin + button_height + margin / 2), 
                              size = (button_width, button_height), 
                              text = "Загрузить", 
                              font_size = 32,
                              action = lambda : self.load_save())

        self.settings_button = Button(pos = (self.screen.get_width() - button_width - margin, margin),
            size = (button_width, button_height), 
            text = "Параметры", 
            font_size = 32,
            action = lambda : self.boot_settings())

        self.start_button = Button(pos = (self.screen.get_width() - button_width - margin, self.screen.get_height() - margin - button_height), 
                size = (button_width, button_height), 
                text = "Запустить", 
                font_size = 32,
                action = lambda : self.experiment.start())

        self.save_settings_button = Button(pos = (self.screen.get_width() - button_width * 2 - margin, margin),
            size = (button_width * 2, button_height), 
            text = "Сохранить параметры", 
            font_size = 32,
            action = lambda : self.deboot_settings())

        self.clear_button = Button(pos = (margin, margin),
            size = (button_width * 2, button_height), 
            text = "Очистить поле", 
            font_size = 32,
            action = lambda : self.clear_field())

        self.spawn_light_source = Button(
            pos = (self.screen.get_width() - button_width * 2 - margin, self.screen.get_height() - margin - button_height),
            size = (button_width * 2, button_height),
            text = "Добавить источник",
            font_size = 32,
            action = lambda : self.experiment.add_light_source(self.experiment.mirrors[0])
        )

        self.edit_light_source_button = Button(
            pos = (self.screen.get_width() - button_width * 2 - margin, self.screen.get_height() - margin - button_height),
            size = (button_width * 2, button_height),
            text = "Изменить источник",
            font_size = 32,
            action = lambda : self.edit_light_source()
        )

        # Кнопки основного режима
        self.exp_mode_buttons = [self.quit_button, self.save_button, self.load_button, self.settings_button, self.start_button]

        # Кнопки режима настроек
        self.settings_mode_buttons = [self.save_settings_button, self.clear_button]

        # Кнопки режима настроек с построенными зеркалами, но без источника света
        self.no_source_buttons = [self.save_settings_button, self.clear_button, self.spawn_light_source]

        # Кнопки режима настроек с построенными зеркалами, с изменением источника света
        self.with_source_buttons = [self.save_settings_button, self.clear_button, self.edit_light_source_button]

    def turn_buttons(self, event, buttons):
        """
            Проверить, была ли нажата кнопка в event из списка buttons, и если да, 
                то выпонлить привязанное к ней действие.
        """

        mouse_x, mouse_y = event.pos

        button_pressed = False
        for button in buttons:
            button_x, button_y = button.pos
            this_button_width, this_button_height = button.size
            if mouse_x >= button_x and mouse_x <= button_x + this_button_width and \
                    mouse_y >= button_y and mouse_y <= button_y + this_button_height:
                if button.is_up:

                    button_pressed = True

                    self.screen.blit(button.down_surface, button.pos)
                    pg.display.flip()
                    button.is_up = False

                    button.action()
        return button_pressed

    def edit_mirror_type(self, mirror):
        """
            Изменить тип зеркала. Запускается окно с выбором типа.
        """

        preselection = None
        if isinstance(mirror, FlatMirror):
            preselection = 0
        elif isinstance(mirror, SphericalMirror):
            if mirror.mirror_type == "concave":
                preselection = 1
            elif mirror.mirror_type == "convex":
                preselection = 2

        choice = easygui.choicebox(
            msg = "Выберите тип зеркала.",
            title = "Изменить тип зеркала",
            choices = ["Плоское", "Вогнутое", "Выпуклое"],
            preselect = preselection
        )

        if choice is not None:
            if choice == "Плоское" and not isinstance(mirror, FlatMirror):

                return FlatMirror(mirror.left_corner, mirror.right_corner)

            elif choice == "Вогнутое":
                if isinstance(mirror, FlatMirror):

                    return SphericalMirror(mirror.left_corner, mirror.right_corner, "concave", 2 * mirror.get_flat_length())

                elif isinstance(mirror, SphericalMirror) and mirror.mirror_type == "convex":
                    
                    return SphericalMirror(mirror.left_corner, mirror.right_corner, "concave", mirror.curv_radius)

            elif choice == "Выпуклое":
                if isinstance(mirror, FlatMirror):

                    return SphericalMirror(mirror.left_corner, mirror.right_corner, "convex", 2 * mirror.get_flat_length())

                elif isinstance(mirror, SphericalMirror) and mirror.mirror_type == "concave":
                    
                    return SphericalMirror(mirror.left_corner, mirror.right_corner, "convex", mirror.curv_radius)
        return None

    def edit_mirror(self, is_button_down, mirror):
        """
            Изменить параметры зеркала. Запускается окно с возможностью изменить все 
                его параметры. Ограничения указываются. 
        """

        experiment = self.experiment

        highlighted = experiment.highlighted

        left_corner, right_corner = mirror.left_corner, mirror.right_corner
        if isinstance(mirror, SphericalMirror):
            radius = mirror.curv_radius

        if is_button_down:

            msg = "Координаты - целые числа от 0 до 1080 по x и до 720 по y\n"\
                    " Свет задаётся в относительном диапазоне [0..1] от левого края;\n"\
                    " направление - от 0 до 180 от правого края против часовой стрелки."
            fields = ["Левый край, x", "Левый край, y", "Правый край, x", "Правый край, y"]
            values = [left_corner[0], left_corner[1], right_corner[0], right_corner[1]]

            if isinstance(mirror, SphericalMirror):
                msg += "\nРадиус кривизны зеркала - от 10e-5 до 1000."
                fields.append("Радиус кривизны")
                values.append(radius)

            newvals = easygui.multenterbox(
                title = "Редактирование зеркала",
                msg = msg,
                fields = fields,
                values = values
            )
            
            while True:
                if newvals is None:
                    break
                errmsg = ""

                for i, value in enumerate(newvals[0:4]):
                    if not value.isdigit() or int(value) < 0 or \
                            ((i == 0 or i == 2) and int(value) > 1080) or \
                            ((i == 1 or i == 3) and int(value) > 720):
                        errmsg = "\n\nОшибка: Координаты - целые числа от 0 до 1080 по x и до 720 по y."
                        break

                if isinstance(mirror, SphericalMirror):
                    radius = newvals[-1]
                    try:
                        radius = float(radius)
                        if radius <= mirror.get_flat_length() / 2 + 1e-5 or radius > 1000:
                            errmsg += "\n\nОшибка. Радиус должен быть больше половины длины между краями"\
                                f"(больше {mirror.get_flat_length() / 2 + 1e-5:.2f}), и ограничен 1000."
                    except ValueError:
                        errmsg += "\n\nОшибка. Радиус - вещественное число."

                if errmsg == "":
                    break
                else:
                    values = [left_corner[0], left_corner[1], right_corner[0], right_corner[1]]
                    if isinstance(mirror, SphericalMirror):
                        values.append(radius)
                    newvals = easygui.multenterbox(
                        title = "Редактирование зеркала",
                        msg = msg + errmsg,
                        fields = fields,
                        values = values
                    )

            if newvals is not None:

                highlighted.left_corner = int(newvals[0]), int(newvals[1])
                highlighted.right_corner = int(newvals[2]), int(newvals[3])
                if isinstance(mirror, SphericalMirror):
                    highlighted.curv_radius = radius
                highlighted.recalculate_points()

                experiment.mirrors[(experiment.mirrors.index(highlighted) - 1) % \
                    len(experiment.mirrors)].right_corner = int(newvals[0]), int(newvals[1])
                experiment.mirrors[(experiment.mirrors.index(highlighted) - 1) % \
                len(experiment.mirrors)].recalculate_points()

                experiment.mirrors[(experiment.mirrors.index(highlighted) + 1) % \
                    len(experiment.mirrors)].left_corner = int(newvals[2]), int(newvals[3])
                experiment.mirrors[(experiment.mirrors.index(highlighted) + 1) % \
                    len(experiment.mirrors)].recalculate_points()

    def edit_destination(self, event_pos):
        """
            Изменить цель. Запуск окна для изменения параметров цели.
        """

        experiment = self.experiment

        mouse_x, mouse_y = event_pos        

        radius = ""
        ldpos = ("","")
        if experiment.light_destination is not None:

            radius = experiment.light_destination.radius
            ldpos = experiment.light_destination.pos
            if (mouse_x - ldpos[0]) ** 2 + (mouse_y - ldpos[1]) ** 2 < radius ** 2:
                newvals = easygui.multenterbox(
                    title = "Редактирование цели",
                    msg = "Координаты - целые числа от 0 до 1080 по x и до 720 по y\n"\
                        " Радиус > 0 и < 200. \n",
                    fields = ["Позиция по x", "Позиция по y", "Радиус"],
                    values = [ldpos[0], ldpos[1], radius]
                )
                while True:
                    if newvals is None:
                        break
                    errmsg = ""

                    new_ldx, new_ldy, new_rad = newvals[0], newvals[1], newvals[2]

                    print(newvals)

                    try:
                        new_ldx = float(new_ldx)
                        new_ldy = float(new_ldy)
                        ldpos = (new_ldx, new_ldy)
                        new_rad = float(new_rad)
                    except ValueError:
                        errmsg += "\n\nОшибка: значения должны быть числами."

                    if new_rad <= 0 or new_rad >= 200:
                        errmsg += "\n\nОшибка: радиус должен быть > 0 и < 200."
                    else:
                        radius = new_rad

                    if errmsg == "":
                        break
                    else:
                        newvals = easygui.multenterbox(
                            title = "Редактирование цели",
                            msg = "Координаты - целые числа от 0 до 1080 по x и до 720 по y\n"\
                                " Радиус > 0.\n" + errmsg,
                            fields = ["Позиция по x", "Позиция по y", "Радиус"],
                            values = [ldpos[0], ldpos[1], radius]
                        )

                del experiment.light_destination
                experiment.light_destination = LightDestination(ldpos, radius)

            else:
                del experiment.light_destination
                experiment.light_destination = LightDestination(event_pos, 10)
        else:
            experiment.light_destination = LightDestination(event_pos, 10)

    def edit_light_source(self):
        """
            Изменить источник света. Запускается окно с изменением параметров света.
        """

        experiment = self.experiment

        light_source = experiment.light_source

        light_pos = experiment.light_source.local_pos
        light_dir = experiment.light_source.light_direction
        light_velocity = experiment.light_source.velocity
        mirror_idx = experiment.mirrors.index(experiment.light_source.mirror)

        msg = "Свет задаётся в относительном диапазоне [0..1] от левого края;\n"\
              " направление - от 0 до 180 от правого края против часовой стрелки.\n"\
              "Также можно выбрать номер зеркала, на которое установить свет (по умолчанию 0)."
        fields = ["Положение света", "Угол выхода", "Скорость распространения", "Номер зеркала"]
        values = [light_pos, light_dir, light_velocity, mirror_idx]

        newvals = easygui.multenterbox(
            title = "Редактирование источника",
            msg = msg,
            fields = fields,
            values = values
        )
        
        while True:
            if newvals is None:
                break
            errmsg = ""

            light_pos = newvals[0]
            light_dir = newvals[1]

            if light_dir != "" or light_pos != "":

                if light_pos != "":
                    if light_dir == "":
                        light_dir = 90.0
                if light_dir != "" and light_pos == "":
                    errmsg += "\n\nОшибка: Задан угол выхода света, но не задано его положение."

                try:
                    light_pos = float(light_pos)
                    if light_pos < 0.0 or light_pos > 1.0:
                        errmsg += "\n\nОшибка: Положение света задается диапазоном [0..1]."
                except ValueError:
                    errmsg += "\n\nОшибка: Положение света задано не числом."

                try:
                    light_dir = float(light_dir)
                    if light_dir < 0.0 or light_dir > 180.0:
                        errmsg += "\n\nОшибка: Угол выхода света задается диапазоном [0..180] "\
                            "от правого края против часовой стрелки."
                except ValueError:
                    errmsg += "\n\nОшибка: Угол выхода света задано не числом."

            light_velocity = newvals[2]

            if light_velocity == "" and light_dir != "":
                light_velocity = 100.0
            elif light_velocity != "" and (light_dir == "" or light_pos == ""):
                errmsg += "\n\nОшибка: Не задано положение света."

            elif light_velocity != "":

                try:
                    light_velocity = float(light_velocity)
                except ValueError:
                    errmsg += "\n\nОшибка: Скорость распространения света задана не числом."

                if light_velocity <= 0.0:
                    errmsg += "\n\nОшибка: Скорость распространения света должна быть > 0."

            mirror_idx = newvals[3]

            if mirror_idx != "":
                try:
                    mirror_idx = int(mirror_idx)
                    if mirror_idx < 0 or mirror_idx >= len(experiment.mirrors):
                        errmsg += f"\n\nОшибка: Такого номера зеркала не существует.\nВыберите значение от 0 до {len(experiment.mirrors) - 1}."
                except ValueError:
                    errmsg += "\n\nОшибка: Номер зеркала задан не числом."

            if errmsg == "":
                break
            else:
                values = [light_pos, light_dir, light_velocity, mirror_idx]

                newvals = easygui.multenterbox(
                    title = "Редактирование зеркала",
                    msg = msg + errmsg,
                    fields = fields,
                    values = values
                )

        if newvals is not None:

            if light_pos != "":
                if light_pos != experiment.light_source.local_pos or \
                   light_dir != experiment.light_source.light_direction:
                    experiment.light_source.local_pos = light_pos
                    experiment.light_source.light_direction = light_dir
            if light_velocity != "":
                experiment.light_source.velocity = light_velocity
            else:
                experiment.light_source.velocity = 80.0
            if mirror_idx != "":
                experiment.light_source.mirror = experiment.mirrors[mirror_idx]
