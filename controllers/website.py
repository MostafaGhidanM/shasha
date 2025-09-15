# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website
import logging

_logger = logging.getLogger(__name__)


class TechDreamWebsite(Website):
    """Enhanced website controller for TechDream theme"""

    # Remove custom homepage route to avoid conflicts - use Odoo's default
    pass