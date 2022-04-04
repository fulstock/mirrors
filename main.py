from classes import Experiment, Window

# Создание окна и эксперимента
def setup():

    exp = Experiment()
    window = Window(exp)
    return exp, window

# Запуск программы
def main():

    exp, window = setup()
    exp.run(window)


if __name__ == "__main__":
    main()
