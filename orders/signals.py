from django.dispatch import Signal

file_uploaded = Signal()
#file_uploaded = Signal(providing_args=['uploaded_file_path'])