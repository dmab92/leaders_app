# -*- coding:utf-8 -*-
import time

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
from odoo.exceptions import Warning, ValidationError
from odoo.tools.translate import _

#
# class res_users(models.Model):
#     _inherit = "res.users"
#     # _name = "res.users"
#
#     center_id = fields.Many2one("leaders.center", string="Centre de Prepas")
#     region = fields.Selection([('ad', 'ADAMAOUA'),
#                                ('ce', 'CENTRE'),
#                                ('en', 'EXTREME-NORD'),
#                                ('es', 'EST'),
#                                ('lt', 'LITTORAL'),
#                                ('no', 'NORD'),
#                                ('nd', 'NORD-OUEST'),
#                                ('ou', 'OUEST'),
#                                ('su', 'SUD'),
#                                ('sd', 'SUD-OUEST'),
#                                ],
#                               string='REGION',
#                               help="La region ou se situe l'etablissement Scolaire")




# class res_company(models.Model):
#     _name = "res.company"
#     _inherit = "res.company"
#
#     type_agence = fields.Selection(string="Type agence", selection=[('none', 'None'), ('first', 'Première catégorie'),
#                                                                     ('second', 'Deuxième catégorie')], default='second')