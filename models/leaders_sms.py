# -*- coding: utf-8 -*-

import openpyxl
import base64
import time
from datetime import datetime
from io import BytesIO
from odoo import api, fields, models, SUPERUSER_ID, _
import urllib, requests
from odoo.exceptions import UserError, Warning, ValidationError


class leaders_sms(models.Model):
    _name = 'leaders.sms'
    _description = 'Envoi des SMS'


    name = fields.Char("Suject")
    #contact_list_ids = fields.Many2many('mailing.list',string=' Liste de diffusion')
    #sender_phone = fields.Char("Numero de Telephone")
    #value2 = fields.Float(compute="_value_pc", store=True)
    date_register = fields.Date("Date d'envoi",default = datetime.today().date())
    message = fields.Text(string="Message")
    state = fields.Selection([('draft', 'Brouillon'),
                              ('valited', 'Validé'),
                              ('cancel', 'Annulé')
                              ], default='draft', string="Etat")
    file = fields.Binary(string="File", required=True)
    line_ids =fields.One2many( 'leaders.sms.line','sms_id', string="Informations sur les recepteurs ")

    def import_customer(self):
        #
            wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.file)), read_only=True)
            ws = wb.active
            #vals=[]
            i=1
            for record in ws.iter_rows(min_row=i, max_row=None, min_col=None, max_col=None, values_only=True):

                #raise UserError(_(len(str(record[1]))))

                # if len(str(record[1]))=12:

                #     raise UserError(_("Desolez !!!  le numero de la ligne %s n'est pas correct",(i)))
                # else:
                vals =  {'name': record[0], 

                            'phone': record[1]}
                #self.env['leaders.sms.line'].create( {'name': record[0], 'phone': record[1]} )
                self.write({'line_ids': [[0, 0, vals]]})
            i+=1
                #raise UserError(_('Please insert a valid file  4'))

        #except:
            #raise UserError(_('Please insert a valid file'))

    def action_send_sms(self):

        # if not self.digital_signature:
        #     raise UserError(_("Veillez faire signer le destinataire du avant de valider la reception"))

        # Notification SMS a  l'expediteur
        

        api_key = 'b0l5cGl6TE5JZmt6ZkdIZEZsTUQ='
        url = 'https://app.techsoft-web-agency.com/sms/api'
        senderID = 'LeadersCorp'
        message = str(self.message)

        for line in self.line_ids:
            destination = str(line.phone)
            sms_body = {
                'action': 'send-sms',
                'api_key': api_key,
                'to': destination,
                'from': senderID,
                'sms': message
            }
            final_url1 = url + "?" + urllib.parse.urlencode(sms_body)
            requests.get(final_url1)

        return self.write({'state': 'valited'})


class leaders_sms_line(models.Model):
    _name = 'leaders.sms.line'
    _description = 'Ligne de d''Envoi des SMS'

    phone = fields.Char("Numero du destinataire")
    name = fields.Char("Nom du destinataire")
    sms_id = fields.Many2one("leaders.sms")



    # @api.constrains('phone')
    # def _check_phone_number(self):
    #     for rec in self:
    #         if rec.phone and len(rec.phone) != 9:
    #             raise ValidationError(_("  Le numero  de Telephone  doit avoir 12 chiffres sans espaces"))

    #     return True
