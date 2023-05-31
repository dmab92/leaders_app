#See LICENSE file for full copyright and licensing details.



from odoo import fields, models,api ,SUPERUSER_ID, _

class ConcourBalancReport(models.TransientModel):
    _name = "concour.blanc.wizard"
    #_rec_name = "date_start"
    _description = " Resultats du concours Blanc"


    @api.model
    def _get_default_academic_year(self):
        academic_year_obj = self.env['leaders.year']
        academic_year_id = academic_year_obj.search([('actived', '=', True)], limit=1)
        return academic_year_id and academic_year_id.id or False

    #name = fields.Char("Noms")
    concour_id = fields.Many2one("leaders.concour.config", string="Concours", required=True)
    #matiere_ids = fields.Many2many("leaders.matier", string="Matières")
    number = fields.Selection([('1', '1'),
                               ('2', '2'),
                               ('3', '3'),
                               ('4', '4'),
                               ('5', '5'),
                               ('6', '6'),
                               ('7', '7'),
                               ('or', 'D''Or'),
                               ], string="Numero du concours Blanc")
    year_id = fields.Many2one("leaders.year", string="Année en cours", required=True,
                              default=lambda self: self._get_default_academic_year())
    center_ids = fields.Many2many("leaders.center", string="Centre de preparation")
    file_name = fields.Char('Nom du fichier', size=255, readonly=True)
    file_data = fields.Binary('File', readonly=True)
    bool = fields.Boolean('Exporté', readonly=True)



    def print_report(self):
        datas = {

                'concour_id': self.concour_id.id,
                'number': self.number,
                'year_id': self.year_id.id,
            }
        return self.env.ref('leaders_app.resultats_concours_xls').report_action(self, data=datas)