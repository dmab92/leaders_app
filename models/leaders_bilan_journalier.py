# -*- coding: utf-8 -*-

# import time
from datetime import datetime
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, Warning, ValidationError


class bilan_journalier(models.Model):
    _name = 'leaders.bilan.journalier'
    _description = 'Bilan Journalier'
    _order = 'id DESC'

    @api.model
    def _get_default_academic_year(self):
        academic_year_obj = self.env['leaders.year']
        academic_year_id = academic_year_obj.search([('actived', '=', True)], limit=1)
        return academic_year_id and academic_year_id.id or False

    name = fields.Char("Nom", compute='_get_name', store=True)
    date = fields.Date("Date", default=datetime.today().date(), required=True)
    center_id = fields.Many2one("leaders.center", string="Centre de Preparation", required=True)
    year_id = fields.Many2one("leaders.year", string="Année Académique",
                              default=lambda self: self._get_default_academic_year())
    total_frais_cour = fields.Integer(string='Montant Entrées Frais de concours', required=True)
    total_livre = fields.Integer(string='Montant Livres Vendus', required=True)
    total_dossier = fields.Integer(string='Montant Entrées Dossiers')
    total_sorti = fields.Integer(string='Total des Sorties', required=True)
    solde = fields.Integer(string='Solde(ENTREE COURS + ENTREES LIVRES - SORTIES)', required=True)
    solde_in_letter = fields.Char("Solde Total en Lettre")
    # sortie_ids = fields.One2many('leaders.sortie', 'bilan_id', string=" Sorties")
    sortie_ids = fields.One2many('leaders.sortie', 'bilan_id', copy=True)
    enseignement_ids = fields.One2many('leaders.enseignement', 'bilan_id', copy=True, string='Section Enseignement')

    amount_verse = fields.Integer("Montant du Versement", help="Il s'agit du monant verse a la banque")
    amount_momo = fields.Integer("Montant OM/MOMO", help="Il s'agit du montant envoye par OM/MOMO")
    amount_phy = fields.Integer("Montant Personne Physique")
    amount_dossier = fields.Integer("MONTANT VERSEMENT DOSSIER")
    employee_momo_id = fields.Many2one('leaders.employee', 'Nom de la personne ayant recu le depot')
    employee_phy_id = fields.Many2one('leaders.employee', "Nom de la Personne Physique Ayant recu ")
    signature_ac = fields.Binary(string="Signature Agent Comptable")
    signature_cf = fields.Binary(string="Signature Chef de centre")
    photo = fields.Binary(string="Image du recu de banque")
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
                               ], string='REGION', related='center_id.region', store='True',
                              help="La region ou se situe le centre de prepaartion")

    state = fields.Selection([('draft', 'Brouillon'),
                              ('valited', 'Validé')
                              ], default='draft', string="Etat")
    bool = fields.Boolean("Je confirme l'exactitude de l'ensemble des Informations inserées sur cette fiche")

    @api.constrains('total_frais_cour','total_livre', 'total_dossier',
                    'amount_verse','amount_momo','amount_phy','amount_dossier')
    def _check_something(self):
        for record in self:
            if record.total_frais_cour < 0 or record.total_livre < 0 or record.total_dossier < 0:
                raise ValidationError("Vous avez un montant  Négatif")
            if record.amount_verse < 0 or record.amount_momo < 0 or record.amount_phy < 0 or record.amount_dossier:
                raise ValidationError("Vous avez un montant  Négatif")
            if not record.solde_in_letter:
                raise ValidationError("Veillez entrer le Solde en Lettre")


    @api.onchange('sortie_ids', 'total_frais_cour', 'total_livre', 'total_dossier')
    def _onchange_total_sorties(self):
        for record in self:
            somme = 0
            for line in record.sortie_ids:
                somme += line.amount
            record.total_sorti = somme
            record.solde = record.total_frais_cour + record.total_livre + record.total_dossier - record.total_sorti

            # sortie_ids_list = record.sortie_ids.filter(lambda r: r.amount)
            # record.total_sorti = sum(sorti.amount for sorti in sortie_ids_list)

    # @api.constrains('total_frais_cour')
    # def _check_phone_number(self):
    #     for rec in self:
    #         if rec.total_frais_cour <0:
    #             raise ValidationError(_("Le Montant total frais de cours ne peut pas etre negatif"))
    #
    #     return True

    @api.depends('center_id', 'date')
    def _get_name(self):
        for record in self:
            record.name = 'BILAN JOURNALIER DU ' + str(record.date) + ' AU CENTRE  ' + str(record.center_id.name)

    def set_to_validated(self):
        for record in self:
            if not record.bool:
                raise UserError(_("Veillez confirmez l'exactitude de l'ensemble des Informations inserées sur cette "
                                  "fiche"))
            if not record.signature_ac:
                raise UserError(_("Désolez !! vous ne pouvez pas valider ce bilan car l'AGENT COMPATBLE ne l'a pas "
                                  "encore signé !! "))
            if not record.signature_cf:
                raise UserError(_("Désolez !! vous ne pouvez pas valider ce bilan car le CHEF DE CENTRE ne l'a pas "
                                  "encore signé !!"))
            else:
                for line in record.enseignement_ids:
                    line.state = 'valited'
                    line.center_id = record.center_id and record.center_id.id
        return self.write({"state": "valited"})

    def set_to_draft(self):
        return self.write({"state": "draft"})

    def loard_data(self):
        # paiement_ids = self.env['leaders.paiement_history'].search([('center_id', '=', self.center_id.id),('year_id', '=', self.year_id.id)])
        dossier_ids = self.env['leaders.paiement_history'].search([('center_id', '=', self.center_id.id),
                                                                   ('date_register', '=', self.date),
                                                                   ('motif', '=', 'frais_dossier'),
                                                                   ('state', '=', 'valited')])

        livre_ids = self.env['leaders.paiement_history'].search([('center_id', '=', self.center_id.id),
                                                                 ('date_register', '=', self.date),
                                                                 ('motif', 'in', ['tome1', 'tome2', 'livre_activite']),
                                                                 ('state', '=', 'valited')])
        frais_ids = self.env['leaders.paiement_history'].search([('center_id', '=', self.center_id.id),
                                                                 ('date_register', '=', self.date),
                                                                 ('motif', 'in',
                                                                  ['inscription', 'tranche1', 'tranche2', 'tranche3']),
                                                                 ('state', '=', 'valited')])

        somme = 0
        for line in dossier_ids:
            somme += line.amount_paid
        for record in self:
            record.total_frais_cour = somme
            # self.write({"total_frais_cour": somme})
            # raise UserError(_(record.total_frais_cour))

    def name_get(self):
        '''Method to display name and code'''
        return [(rec.id, ' BILAN Journalier du ' + str(rec.date) + ' du Centre ' + str(rec.center_id.name)) for rec in
                self]


class sorti_journalier(models.Model):
    _name = 'leaders.sortie'
    _description = 'Sortie Journalieres'
    _order = 'id DESC'
    _rec_name = 'motif'

    amount = fields.Integer(string='Montant', required=True)
    motif = fields.Char("Motif")
    employee_id = fields.Many2one('leaders.employee', 'Personne Ayant Autorisé',required=True)
    date_register = fields.Date("Date Sortie", related='bilan_id.date',required=True)
    total_sorti = fields.Integer(string='Montant')
    bilan_id = fields.Many2one('leaders.bilan.journalier')
    center_id = fields.Many2one("leaders.center", string="Centre de preparation", related='bilan_id.center_id')


class journal_enseignement(models.Model):
    _name = 'leaders.enseignement'
    _description = 'Section Enseigenement '
    _order = 'id DESC'

    name = fields.Many2one("leaders.employee", string="Nom de l'enseignant", required=True)
    matier_id = fields.Many2one("leaders.matier", string='Matière', required=True)
    signature_cf = fields.Binary(string="Signature")
    date = fields.Date("Date du cours", default=datetime.today().date(),required=True)
    time_start = fields.Float(string='Heure de Debut')
    time_end = fields.Float(string='Heure de fin')
    time_dif = fields.Float("Nombre d'Heures", compute='compute_time_dif', store=True)

    # date_end = fields.Datetime("Date de Fin")
    blouse = fields.Selection([('yes', 'OUI'),
                               ('no', 'NON')
                               ], string="Port de Blouse ")
    bilan_id = fields.Many2one('leaders.bilan.journalier')

    contenu = fields.Char("Titre des Contenus")
    observation = fields.Char("Observations")
    center_id = fields.Many2one("leaders.center", string="Centre de preparation", related='bilan_id.center_id',required=True)

    state = fields.Selection([('draft', 'Brouillon'),
                              ('valited', 'Validé'), ('cancel', 'Annulé')
                              ], default='draft', string="Etat")

    salle = fields.Selection([('1', 'Salle 1'),
                              ('2', 'Salle 2'),
                              ('3', 'Salle 3'),
                              ('4', 'Salle 4'),
                              ('5', 'Salle 5'),
                              ('6', 'Salle 6'),
                              ('7', 'Salle 7'),
                              ('8', 'Salle 8'),
                              ('9', 'Salle 9'),
                              ('10', 'Salle 10'),
                              ], required=True,
                             string='Salle')

    @api.depends('time_start', 'time_end')
    def compute_time_dif(self):
        for record in self:
            record.time_dif = record.time_end - record.time_start
        # if self.time_start and self.time_end:
