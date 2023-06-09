# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, Warning, ValidationError


class leaders_paiement(models.Model):
    _name = 'leaders.paiement'
    _description = 'Les informations de paiement'
    _rec_name = 'apprenant_id'
    _order = 'id DESC'

    def _get_nex_reference(self):
        query = """SELECT COUNT(id) AS ligne FROM leaders_paiement"""
        self.env.cr.execute(query)
        data = self.env.cr.fetchone()[0]
        year = time.strftime('%Y')
        sort_year = ''

        # on recupère les 2 derniers chiffres
        y = 0
        for i in year:
            y += 1
            if y < 3:
                continue
            sort_year = sort_year + str(i)

        if not data or data == 0:
            return 'TICKET/0001/' + sort_year

        if data < 10:
            return 'TICKET/000' + str(data + 1) + '/' + sort_year

        if data < 100 and data >= 10:
            return 'TICKET/00' + str(data + 1) + '/' + sort_year

        if data < 1000 and data >= 100:
            return 'TICKET/0' + str(data + 1) + '/' + sort_year

        if data < 10000 and data >= 1000:
            return 'TICKET' + str(data + 1) + '/' + sort_year

    @api.model
    def _get_default_academic_year(self):
        academic_year_obj = self.env['leaders.year']
        academic_year_id = academic_year_obj.search([('actived', '=', True)], limit=1)
        return academic_year_id and academic_year_id.id or False

    date_register = fields.Datetime("Date premier versement", default=datetime.now())
    apprenant_id = fields.Many2one("leaders.apprenant", string="Apprenant")
    matricule = fields.Char("Matricule", related='apprenant_id.matricule' , store=True)
    user_id = fields.Many2one('res.users', 'Recu par', default=lambda self: self.env.user)
    payment_number = fields.Char(string="Numero du recu", default=lambda self: self._get_nex_reference())
    #concour_ids = fields.Many2many("leaders.concour.config", string="Concours",  required=True)
    concour_ids = fields.Many2many("leaders.concour.config",'paiement_id', related='apprenant_id.concours_ids',
                                    string="CONCOURS")
    center_id = fields.Many2one("leaders.center", related='apprenant_id.center_id', string="Centre de Préparation")
    year_id = fields.Many2one("leaders.year", string="Année Académique",
                              default=lambda self: self._get_default_academic_year())
    remaining_amount = fields.Integer(string='Montant Restant',compute='_compute_remaining_amount')
    total_amount = fields.Integer(string='Montant restant')
    signature = fields.Binary(string="Signature  de l'apprenant lors de la reception du livre")
    ligne_paiement_ids = fields.One2many('leaders.ligne_paiement', 'paiement_id', string="  liste des paiements")
    paiement_history_ids = fields.One2many('leaders.paiement_history', 'paiement_id',
                                           string="Hsitoriques des paiements")
    amount_to_paid = fields.Integer(string="Montant  à Payer Arrété avec l'AC")

    confirmation = fields.Boolean("Je Confirme que ces informations sont correctes ")

    state = fields.Selection([('draft', 'Brouillon'),
                              ('valited', 'Validé'),
                              ], default='draft', string="Etat")

    @api.constrains('amount_to_paid', 'remaining_amount')
    def _check_something(self):
        for record in self:
            if record.amount_to_paid < record.remaining_amount:
                raise ValidationError("Le Montant restant ne peut pas etre superieur "
                                      "au Montant  à Payer Arrété avec l'AC ")
            if record.amount_to_paid < 0 or record.remaining_amount < 0:
                raise ValidationError("Vous avez un montant  Négatif")

    @api.depends('amount_to_paid','ligne_paiement_ids')
    def _compute_remaining_amount(self):
        for rec in self:
            som = 0
            for line in rec.ligne_paiement_ids:
                if line.motif in ['inscription','tranche1','tranche2','tranche3']:
                    som += line.amount_paid
            rec.remaining_amount = rec.amount_to_paid-som

    # @api.onchange('apprenant_id')
    # def _onchange_apprenant_id(self):
    #     for rec in self:
    #         if rec.apprenant_id:
    #             rec.center_id = rec.apprenant_id.center_id and rec.apprenant_id.center_id.id
    #             rec.matricule = rec.apprenant_id.matricule

    def set_to_validated(self):
        for record in self:
            if not record.ligne_paiement_ids:
                raise UserError(_("'Alert !!!  vous n'avez enregistrer aucun  motif de paiement'"))
            if not record.confirmation:
                raise UserError(_("'Alert  !!!  Avant de valider ce paiement "
                                  "vous devez confirmer l'exactitude des montants  que vous avez fourni car cette "
                                  "Opération est irreverssible '"))
            else:
                for ligne in record.ligne_paiement_ids:
                    if ligne.state == 'draft':
                        vals = {
                            'motif': ligne.motif,
                            'amount_paid': ligne.amount_paid,
                            'apprenant_id': record.apprenant_id and record.apprenant_id.id,
                            'center_id': record.center_id and record.center_id.id,
                            #'concour_ids': record.concour_ids and record.concour_ids.ids,
                            'user_id': record.user_id and record.user_id.id,
                            'date_register': record.date_register,
                            'matricule': record.matricule,
                            'state': 'valited',
                            'payment_number': record.payment_number,
                            'paiement_id': self.id
                        }
                        record.write({'paiement_history_ids': [[0, 0, vals]]})
                    ligne.write({"state": 'valited'})
                    #record.ligne_paiement_ids = False
        return self.write({"state": 'valited'})

    def set_to_draft(self):
        return self.write({"state": 'draft'})

    # def print_recu(self):
    #     for rec in self:
    #         rec.ligne_paiement_ids = False
    #     return self.env.ref('leaders_app.action_report_recu_paiement').report_action(self)


class ligne_paiement(models.Model):
    _name = 'leaders.ligne_paiement'
    _description = 'Lignes de paiement'
    _order = 'id DESC'

    motif = fields.Selection([('inscription', 'Inscription'),
                              ('frais_dossier', 'Frais dossier'),
                              ('tranche1', 'Première Tranche'),
                              ('tranche2', 'Deuxième Tranche'),
                              ('tranche3', 'Troisième Tranche'),
                              ('tome1', ' Livre tome 1'),
                              ('tome2', 'Livre tome 2'),
                              ('livre_activite', 'Livre de Prépa')], required=True, string='Motif du paiement')
    amount_paid = fields.Integer(string='Montant versé', required=True)
    concour_id = fields.Many2one("leaders.concour.config", string="Concours")
    date_register = fields.Datetime("Date de paiement", default=datetime.now())

    paiement_id = fields.Many2one('leaders.paiement')
    state = fields.Selection([('draft', 'Brouillon'),
                              ('valited', 'Validé'),
                              ], default='draft', string="Etat")
    payment_number = fields.Char(string="Numero du recu")


class paiement_history(models.Model):
    _name = 'leaders.paiement_history'
    _description = 'Historiques des payement de l''apprenant'
    _order = 'id DESC'
    _rec_name = 'apprenant_id'

    apprenant_id = fields.Many2one("leaders.apprenant", string="Apprenants")
    #concour_id = fields.Many2one("leaders.concour.config", string="Concours")
    #concour_ids = fields.Many2many("leaders.concour.config", "Concours",  required=True)

    center_id = fields.Many2one("leaders.center", string="Centre de preparation choisi")
    year_id = fields.Many2one("leaders.year", string="Année Académique")
    motif = fields.Selection([('inscription', 'Inscription'),
                              ('frais_dossier', 'Frais dossier'),
                              ('tranche1', 'Première Tranche'),
                              ('tranche2', 'Deuxième Tranche'),
                              ('tranche3', 'Troisième Tranche'),
                              ('tome1', ' Livre tome 1'),
                              ('tome2', 'Livre tome 2'),
                              ('livre_activite', 'Livre de Prépas')], string='Motif du paiement')
    amount_paid = fields.Integer(string='Montant versé')

    paiement_id = fields.Many2one('leaders.paiement')
    remaining_amount = fields.Integer(string='Montant restant')
    user_id = fields.Many2one('res.users', 'Recu par')
    date_register = fields.Datetime("Date de paiement")
    payment_number = fields.Char(string="Numero du recu")
    matricule = fields.Char("Matricule")
    year_id = fields.Many2one("leaders.year", string="Année Académique",
                              default=lambda self: self._get_default_academic_year())
    state = fields.Selection([('draft', 'Brouillon'),
                              ('valited', 'Validé'),
                              ], default='draft', string="Etat")

    @api.model
    def _get_default_academic_year(self):
        academic_year_obj = self.env['leaders.year']
        academic_year_id = academic_year_obj.search([('actived', '=', True)], limit=1)
        return academic_year_id and academic_year_id.id or False
