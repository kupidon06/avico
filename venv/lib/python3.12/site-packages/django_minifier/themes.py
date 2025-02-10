from django.template.loaders.app_directories import Loader as AppDirectoriesLoader
from django.template.utils import get_app_template_dirs
from .mixins import TemplateMinifierMixin


class Loader(TemplateMinifierMixin, AppDirectoriesLoader):
    def get_dirs(self):
        return get_app_template_dirs("themes")
