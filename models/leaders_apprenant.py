# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api


class leaders_apprenant(models.Model):
    _name = 'leaders.apprenant'
    _description = ' Les apprenants de leaders'
    _order = 'id DESC'

    def _get_next_reference(self):
        query = """SELECT COUNT(id) AS ligne FROM leaders_apprenant"""
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
            return 'MAT/0001/' + sort_year

        if data < 10:
            return 'MAT/000' + str(data + 1) + '/' + sort_year

        if data < 100 and data >= 10:
            return 'MAT/00' + str(data + 1) + '/' + sort_year

        if data < 1000 and data >= 100:
            return 'MAT/0' + str(data + 1) + '/' + sort_year

        if data < 10000 and data >= 1000:
            return 'MAT' + str(data + 1) + '/' + sort_year


    @api.model
    def _get_default_academic_year(self):
        academic_year_obj = self.env['leaders.year']
        academic_year_id = academic_year_obj.search([('actived', '=', True)], limit=1)
        return academic_year_id and academic_year_id.id or False


    name = fields.Char("Noms et Prenoms", required=True)
    date_register = fields.Date("Date d'enregistrement",default = datetime.today().date())
    matricule = fields.Char("Matricule",default = lambda self: self._get_next_reference())

    etablissment_id = fields.Many2one("leaders.school", string="Etablissement Frequenté")
    #actuel_school_id= fields.Many2one("leaders.school", string=" Etablissement Actuel")
    is_student = fields.Boolean("Etes vous un etudiant ?", default=False)
    univ_id = fields.Many2one("leaders.school", string="Université")
    class_id = fields.Many2one("leaders.class", string="Classe/Niveau")
    filiere_id = fields.Many2one("leaders.filiere", string="Filière")
    phone_apprenant = fields.Char("Téléphone")
    whatsap_phone= fields.Char("Numéro Whatsapp")
    quarter_live = fields.Char("Quartier de residence")
    serie_terminal = fields.Char("Serie éffectué en Terminale ")
    concours_ids = fields.Many2many("leaders.concour.config", string="CONCOURS SOLLICITES (Uniquement les concours pour lesquels il va payer)")
    #serie_terminal_id = fields.Many2one("leaders.speciality", String="Serie éffectué en Terminale")
    father_work_id = fields.Many2one("leaders.work", string="Profession du Père")
    mother_work_id = fields.Many2one("leaders.work",string="Profession de la Mère")
    parent_town_id= fields.Many2one("leaders.town",string="Ville de  Résidence des parents")
    center_id = fields.Many2one("leaders.center", string="Centre de preparation choisi", required=True)
    phone_parents = fields.Char(" Contact des Parents/Tuteurs")
    photo = fields.Binary(string="photo")

    year_id = fields.Many2one("leaders.year", string ="Année Académique",default=lambda self: self._get_default_academic_year())
    #
    q1 = fields.Selection([('oui', 'OUI'),('non', 'NON'), ], string='A cause d’une conférence dans ton établissement')
    q2 = fields.Selection([('oui', 'OUI'), ('non', 'NON'), ], string='A cause des statistiques de performances de leader’s corporation')
    q3 = fields.Selection([('oui', 'OUI'), ('non', 'NON'), ], string='A cause du Leader’s challenge')
    q4 = fields.Selection([('oui', 'OUI'), ('non', 'NON'), ], string='A cause d’un particulier (membre de leader’s, parent, ami, ainé …)')
    q5 = fields.Char("Si oui préciser un détail permettant d’identifier le particulier (Tel ou nom ou fonction…)")
    q6 = fields.Selection([('oui', 'OUI'), ('non', 'NON'), ], string='A cause des activités sur WhatsApp')
    q7 = fields.Selection([('oui', 'OUI'), ('non', 'NON'), ], string='A cause des activités sur Facebook')
    q8 = fields.Selection([('oui', 'OUI'), ('non', 'NON'), ], string='A cause des activités par sms')
    q9 = fields.Selection([('oui', 'OUI'), ('non', 'NON'), ], string='As-tu fais les préparations aux concours l’année dernière ?')
    q10 = fields.Char(string="Si oui dans quel groupe")
    dossier = fields.Selection([('oui', 'OUI'), ('non', 'NON'), ], string='CONSTITUTION DES DOSSIERS')
    voyage = fields.Selection([('oui', 'OUI'), ('non', 'NON'), ], string='VOYAGE POUR L’ETRANGER')
    digital_signature = fields.Binary(string=" ", help="Signature de l'eleve")

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
                              string='REGION', related='center_id.region',
                              help="La region ou se situe le centre de prepaartion")



    # @api.model_create_multi
    # def create(self, vals_list):
    #
    #     return super().create(vals_list)



class tranfert_apprenant(models.Model):
    _name = 'leaders.transfert'
    _description = "Les Transferts d'apprenant "

    old_center_id = fields.Many2one("leaders.center", string="Centre de preparation Actuel", required=True)

    new_center_id = fields.Many2one("leaders.center", string="Nouveau centre de preparation", required=True)

    apprenant_id = fields.Many2one("leaders.apprenant", string="Apprenant", required=True)
    state = fields.Selection([('draft', 'Brouillon'),
                              ('valited', 'Validé'),
                              ('cancel', 'Annuler')
                              ], default='draft', string="Etat")

    @api.onchange('apprenant_id')
    def _onchange_apprenant_id(self):
        for rec in self:
            if rec.apprenant_id:
                rec.old_center_id = rec.apprenant_id.center_id and rec.apprenant_id.center_id.id


    def set_to_validated(self):
        for record in self:
            if record.old_center_id:
                record.apprenant_id.center_id = record.new_center_id and record.new_center_id.id

        return self.write({"state": 'valited'})

    def set_to_draft(self):
        return self.write({"state": 'draft'})





