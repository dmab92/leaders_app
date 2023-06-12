# -*- coding: utf-8 -*-


from odoo import models, fields, api, SUPERUSER_ID, _
from odoo import models
from odoo.exceptions import UserError, Warning, ValidationError


class ReportConcours(models.AbstractModel):
    _name = 'report.leaders_app.report_results_xls'
    _inherit = 'report.report_xlsx.abstract'

    @api.model
    def _get_default_academic_year(self):
        academic_year_obj = self.env['leaders.year']
        academic_year_id = academic_year_obj.search([('actived', '=', True)], limit=1)
        return academic_year_id and academic_year_id.id or False

    # name = fields.Char("Noms")
    concour_id = fields.Many2one("leaders.concour.config", string="Concours", required=True)
    number = fields.Selection([('1', '1'),
                               ('2', '2'),
                               ('3', '3'),
                               ('4', '4'),
                               ('5', '5'),
                               ('6', '6'),
                               ('6', '6'),
                               ('7', 'D''Or'),
                               ], string="Numéro du Concours Blanc", required=True)

    year_id = fields.Many2one("leaders.year", string="Année en cours", required=True,
                              default=lambda self: self._get_default_academic_year())
    center_ids = fields.Many2many("leaders.center", string="Centre de preparation")
    file_name = fields.Char('Nom du fichier', size=255, readonly=True)
    file_data = fields.Binary('File', readonly=True)
    bool = fields.Boolean('Exporté', readonly=True)

    def generate_xlsx_report(self, workbook, datas, lines):
        domain = []
        concour_id2 = self.env['leaders.concour.config'].browse(datas.get('concour_id'))
        # concour_id = concour_obj.browse(datas.get('concour_id'))
        concour_id = datas.get('concour_id')
        if datas.get('concour_id'):
            domain += [('concour_id', '=', concour_id)]
        number = datas.get('number')
        if datas.get('number'):
            domain += [('number', '=', number)]
        year_id = datas.get('year_id')
        if datas.get('year_id'):
            domain += [('year_id', '=', year_id)]
        domain += [('state', '=', 'valited')]
        # order = 'user_id desc
        # orderby = "average DESC"
        ligne_concours_ids = self.env['leaders.concour.blanc.line'].search(domain, order="average desc")

        # format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 12, 'align': 'vcenter'})
        sheet = workbook.add_worksheet("RESULTATS  CONCOURS BLANCS")
        data = [
            [' ',
             u' RESULTATS CONCOURS BLANC  No ' + str(number) + '  DE ' + str(concour_id2.name)],
            [' '],
            [u'RANG', u'CENTRE', u'NOMS ET PRENOMS DE L''APPRENANT ', u'DERNIER ETABLISSEMENT FREQUENTE', u'NOTE EPREUVE 1',
             u'NOTE EPREUVE 2', u'NOTE EPREUVE 3', u'NOTE EPREUVE 4',
             u'MOYENNE']
        ]
        indis = 1
        for ligne in ligne_concours_ids:
            data.append([indis,
                         ligne.apprenant_id.center_id.name,
                         ligne.apprenant_id.name,
                         ligne.etablissment_id.name,
                         ligne.note_mat1,
                         ligne.note_mat2,
                         ligne.note_mat3,
                         ligne.note_mat4,
                         ligne.average,
                         ])
            indis = indis + 1
            # On ecris le data dans les lignes et colones du fichiers excel
        for i in range(len(data)):
            for j in range(len(data[i])):
                if j < len(data[i]):
                    sheet.write(i, j, data[i][j], format2)
