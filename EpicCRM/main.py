import os
import django


def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EpicCRM.settings")
    django.setup()


setup_django()

from views.main_view_cli import MainViewCLI
from services.services_crm import ServicesCRM
from controllers.main_controller_crm import MainControllerCRM


def main():
    main_controller = MainControllerCRM()
    main_controller.start()


if __name__ == "__main__":
    main()
