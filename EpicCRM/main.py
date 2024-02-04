import os
import django


def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EpicCRM.settings")
    django.setup()


setup_django()

from views.MainViewCLI import MainViewCLI
from services.ServicesCRM import ServicesCRM
from controllers.MainControllerCRM import MainControllerCRM


def main():
    main_controller = MainControllerCRM()
    main_controller.start()


if __name__ == "__main__":
    main()
