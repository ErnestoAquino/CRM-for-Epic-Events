import os
import django


def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EpicCRM.settings")
    django.setup()


setup_django()

from views.ViewCLI import ViewCLI
from services.ServicesCRM import ServicesCRM
from controllers.ControllerCRM import ControllerCRM


def main():
    controller = ControllerCRM()
    controller.create_collaborator()


if __name__ == "__main__":
    main()
