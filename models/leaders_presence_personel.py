# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api


class leaders_presence_personnel(models.Model):
    _name = 'leaders.presence.personnel'
    _description = 'Enregitrer la presence du personnel'

    @api.model
    def _get_default_academic_year(self):
        academic_year_obj = self.env['leaders.year']
        academic_year_id = academic_year_obj.search([('actived', '=', True)], limit=1)
        return academic_year_id and academic_year_id.id or False

    name = fields.Char("Nom", compute="_generate_name", store=True)
    center_id = fields.Many2one("leaders.center", string="Centre de Prepas")
    date = fields.Date("Date du jour", default=datetime.today().date())
    year_id = fields.Many2one("leaders.year", string="Année Académique",
                              default=lambda self: self._get_default_academic_year())
    # academic_year = fields.Char(string='Année académique', required=True)
    ligne_presence_ids = fields.One2many('leaders.ligne.presence', 'presencepersonnel_id',
                                         string="  liste des presences")

    @api.depends("center_id", "date")
    def _generate_name(self):
        for l in self:
            l.name = 'Presence Personnel  au' + str(l.center_id.name) + 'le ' + fields.Date.from_string(l.date).strftime('%d/%m/%Y')

class leaders_ligne_presence(models.Model):
    _name = 'leaders.ligne.presence'
    _description = 'Enregitrer les informations sur la presence du personnel'

    employee_id = fields.Many2one('leaders.employee', "Nom du Personnel ",require=True, domain=[('type','not in','teacher')])

    job_id = fields.Many2one('hr.job', string='Poste du personnel')
    arriving_time = fields.Float(string="Heure d'arrivé", required=True)
    departure_time = fields.Float(string='Heure de depart', required=True)
    signature = fields.Binary(string='Signature  du personnel')
    time_dif = fields.Float("Nombre d'Heures", compute='compute_time_dif', store=True)
    presencepersonnel_id = fields.Many2one('leaders.presence.personnel')

    @api.depends('arriving_time', 'departure_time')
    def compute_time_dif(self):
        for record in self:
            record.time_dif = record.departure_time - record.arriving_time
