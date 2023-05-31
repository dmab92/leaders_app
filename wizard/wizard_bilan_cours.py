#See LICENSE file for full copyright and licensing details.


from datetime import datetime
from odoo import fields, models,api ,SUPERUSER_ID, _

class BilanEnseignantReport(models.TransientModel):
    _name = "bilan.enseignant.wizard"
    #_rec_name = "date_start"
    _description = " Bilan des Enseignants "


    @api.model
    def _get_default_academic_year(self):
        academic_year_obj = self.env['leaders.year']
        academic_year_id = academic_year_obj.search([('actived', '=', True)], limit=1)
        return academic_year_id and academic_year_id.id or False

    date_start = fields.Date("Date de debut", default=datetime.today().date())
    date_end  = fields.Date("Date de fin")

    year_id = fields.Many2one("leaders.year", string="Année en cours", required=True,
                              default=lambda self: self._get_default_academic_year())

    file_name = fields.Char('Nom du fichier', size=255, readonly=True)
    file_data = fields.Binary('File', readonly=True)
    bool = fields.Boolean('Exporté', readonly=True)



    def print_report(self):
        datas = {

                'date_start': self.date_start,
                'date_end': self.date_end,
                'year_id': self.year_id.id,
            }
        return self.env.ref('leaders_app.blian_cours_xls').report_action(self, data=datas)