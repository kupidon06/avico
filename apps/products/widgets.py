from django.forms.widgets import ClearableFileInput

class CustomClearableFileInput(ClearableFileInput):
    template_name = 'widgets/custom_clearable_file_input.html'

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'multiple' not in self.attrs:
            self.attrs['multiple'] = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['multiple'] = True
        return context
