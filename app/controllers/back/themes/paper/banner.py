from .base import base
from app.models.banner import banner as banner_model


class banner(base):
    url = ['banner']
    metadata = {'title': 'banner', 'modulo': 'banner'}
    breadcrumb = []

    def __init__(self):
        super().__init__(banner_model)
