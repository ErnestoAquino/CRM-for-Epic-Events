import os
import django
import sentry_sdk
import json

secrets_file_path = os.path.join(os.path.dirname(__file__), 'secrets.json')

with open(secrets_file_path) as secret_file:
    secrets = json.load(secret_file)

sentry_dsn = secrets.get("SENTRY_DSN")

sentry_sdk.init(
    dsn = sentry_dsn,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


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
    # division_by_zero = 1 / 0
    main()
