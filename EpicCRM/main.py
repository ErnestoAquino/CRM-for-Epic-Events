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
    user = controller.authenticate_collaborator()
    if user:
        pass


if __name__ == "__main__":
    main()
