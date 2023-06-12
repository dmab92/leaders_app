# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, Warning, ValidationError

class leaders_concours_blanc(models.Model):
    _name = 'leaders.concour.blanc'
    _description = 'Concours Blanc'
    _order = 'id DESC'
    @api.model
    def _get_default_academic_year(self):
        academic_year_obj = self.env['leaders.year']
        academic_year_id = academic_year_obj.search([('actived', '=', True)], limit=1)
        return academic_year_id and academic_year_id.id or False

    name = fields.Char("Nom",compute='_get_name',store=True)
    date_concours = fields.Date("Date du concours", required=True)
    concour_id = fields.Many2one("leaders.concour.config", string="Concours", required=True)
    nb_matier = fields.Char(string="Nombre de d'Epreuves", related='concour_id.nb_matier')
    matiere_ids = fields.Many2many("leaders.matier", string="Matières")

    number = fields.Selection([('1', '1'),
                               ('2', '2'),
                               ('3', '3'),
                               ('4', '4'),
                               ('5', '5'),
                               ('6', '6'),
                               ('7', '7'),
                               ('or', 'D''Or'),
                               ], require=True, string="Numero du concours Blanc")
    state = fields.Selection([('draft', 'Brouillon'),
                               ('valited', 'Validé'),
                               ('cancel', 'Annuler')
                               ],  default='draft', string="Etat")

    year_id = fields.Many2one("leaders.year", string="Année en cours", required=True,
                              default=lambda self: self._get_default_academic_year())
    center_id = fields.Many2one("leaders.center", string="Centre de preparation", required=True)
    lignes_ids = fields.One2many('leaders.concour.blanc.line', 'concour_blanc_id', copy=True, string="Les Apprenants")
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
                               ], string='REGION', related='center_id.region',
                              help="La region ou se situe le centre de prepaartion")


    @api.depends('concour_id','date_concours','number')
    def _get_name(self):
        for record in self:
            record.name = 'Concours Blanc No ' + str(record.number) + ' de ' + str(record.concour_id.name) + ' du Centre  '+str(record.center_id.name)

            #record.name = 'Concours Blanc No ' + str(record.number) + ' de ' + str(record.concour_id.name) + ' du ' + str(record.date_concours)
            #record.name = 'Concours BLanc No ' + str(record.number) + ' De '+str(record.concour_id.name) +' le ' + fields.Date.from_string(
                #record.date_concours).strftime('%d/%m/%Y')
    def set_to_validated(self):
        for record in self:
            for line in record.lignes_ids:

                line.concour_id = record.concour_id.id
                line.year_id = record.year_id.id
                line.center_id = record.center_id.id
                line.etablissment_id = line.apprenant_id.etablissment_id.id
                line.number = record.number
                line.average = float(line.note_mat1 + line.note_mat2 +
                                           line.note_mat3 +
                                           line.note_mat4)/ float((record.concour_id.nb_matier))
                line.state = 'valited'

        return self.write({"state": 'valited'})

    # raise UserError(_("Alerte! la moyenne de cet élève est "
    #                   "superieure a la note minimale requise  pour l'admision en classe superieure"))
    def set_to_draft(self):
        # for record in self:
        #     if record.annuel_average > record.classe_id.min_average:
        #         raise UserError(_("Alerte! la moyenne de cet élève est "
        #                           "superieure a la note minimale requise  pour l'admision en classe superieure"))
        return self.write({"state": 'draft'})

    def set_to_delete(self):
        # for record in self:
        #     if record.annuel_average > record.classe_id.min_average:
        #         raise UserError(_("Alerte! la moyenne de cet élève est "
        #                           "superieure a la note minimale requise  pour l'admision en classe superieure"))
        return self.write({"state": 'cancel'})


    def name_get(self):
        '''Method to display name and code'''
        return [(rec.id, 'Concours Blanc No' + str(rec.number) + '-' + str(rec.concour_id.name)) for rec in self]

    def load_contours_trainer(self):

        lignes_ids = self.env['leaders.apprenant'].search([('center_id', '=', self.center_id.id),
                                                           ('year_id', '=', self.year_id.id),
                                                           ('concours_ids', 'in', self.concour_id.id)
                                                           ])
        if len(lignes_ids) == 0:
            raise UserError(_("'Alert !!! Il n'ya pas d'apprenant remplissant  les critères insérés'"))
        # if not self.concour_id or not self.center_id:
        #     raise UserError(_("'Alert !!! veillez remplir tous les champs obligatoires '"))

        for rec in self:
            if rec.concour_id:
                lines = [(5, 0, 0)]
                for line in lignes_ids:
                    vals = {
                        'apprenant_id': line.id,
                        'etablissment_id': line.etablissment_id.id,
                        'center_id': line.center_id.id
                    }
                    lines.append((0, 0, vals))
                rec.lignes_ids = lines

class leaders_concours_blanc_line(models.Model):
    _name = 'leaders.concour.blanc.line'
    _description = ' Ligne de Concours Blanc'
    _order = 'id DESC'
    _rec_name = 'name'

    @api.model
    def _get_default_academic_year(self):
        academic_year_obj = self.env['leaders.year']
        academic_year_id = academic_year_obj.search([('actived', '=', True)], limit=1)
        return academic_year_id and academic_year_id.id or False
    name = fields.Char("Nom")
    apprenant_id = fields.Many2one("leaders.apprenant", string="Apprenant")
    note_mat1 = fields.Float("Note Epreuve 1 ")
    note_mat2 = fields.Float("Note Epreuve 2 ")
    note_mat3 = fields.Float("Note Epreuve 3 ")
    note_mat4 = fields.Float("Note Epreuve 4 ")
    average = fields.Float("Moyenne",  readonly=1)
    concour_blanc_id = fields.Many2one("leaders.concour.blanc", string="Concour Blanc")
    concour_id = fields.Many2one("leaders.concour.config", string="Concours")
    center_id = fields.Many2one("leaders.center", string="Centre de préparation")
    etablissment_id = fields.Many2one("leaders.school", string="Etablissement Fréquenté")
    number = fields.Selection([('1', '1'),
                               ('2', '2'),
                               ('3', '3'),
                               ('4', '4'),
                               ('5', '5'),
                               ('6', '6'),
                               ('7', '7'),
                               ('or', 'D''Or'),
                               ], string="Numéro du concours Blanc")
    year_id = fields.Many2one("leaders.year", string="Année en cours",
                              default=lambda self: self._get_default_academic_year())

    state = fields.Selection([('draft', 'Brouillon'),
                              ('valited', 'Validé'),
                              ('cancel', 'Annulé')
                              ], string="Etat")






