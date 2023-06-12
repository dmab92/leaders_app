# -*- coding:utf-8 -*-
import time

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
from odoo.exceptions import Warning, ValidationError
from odoo.tools.translate import _

#




# class res_company(models.Model):
#     _name = "res.company"
#     _inherit = "res.company"
#
#     type_agence = fields.Selection(string="Type agence", selection=[('none', 'None'), ('first', 'Première catégorie'),
#                                                                     ('second', 'Deuxième catégorie')], default='second')