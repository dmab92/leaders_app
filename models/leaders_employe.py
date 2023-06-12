# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api

class leaders_employee(models.Model):
    _name = 'leaders.employee'
    _inherit = ['hr.employee']
    _description = ' Les  Employés de Leaders'
    _order = 'id DESC'

    name_affich = fields.Char(string="Nom qui s'affiche")
    post_travail = fields.Char(string="Poste de Travail")
    #is_teacher = fields.Boolean("Est'il un enseignant ?")

    type = fields.Selection([('teacher', 'Enseignant'),
                             ('perma', 'Employé permanant'),
                             ('temp', 'Employé Temporaire'),
                             ], string="Type d'employé", required=True)

    matiere_ids = fields.Many2many("leaders.matier", string="Matières Enseignées")
    univ_id = fields.Many2one("leaders.school", string="Université", required=True)
    center_id = fields.Many2one("leaders.center", string="Centre de preparation")

    phone_empl = fields.Char(" Numero MOMO/OM")
    region = fields.Selection([('ad', 'ADAMAOUA'),
                               ('ce', 'CENTRE'),
                               ('en', 'EXTREME-NORD'),
                               ('es', 'EST'),
                               ('lt', 'LITTORAL'),
                               ('no', 'NORD'),
                               ('nd', 'NORD-OUEST'),
                               ('ou', 'OUEST'),
                               ('su', 'SUD'),
                               ('sd', 'SUD-OUEST'),
                               ],
                              string='REGION', required=True,
                              help="La region ou se situe le centre de prepaartion")
    category_ids = fields.Many2many(
        'hr.employee.category', 'student_category_rel',
        'student_id', 'category_id',
        string='Tags')








