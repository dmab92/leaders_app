# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
import urllib, requests
from odoo.exceptions import UserError, Warning, ValidationError

class leaders_sms(models.Model):
    _name = 'leaders.sms'
    _description = 'Envoi des SMS'


    name = fields.Char("Suject")
    contact_list_ids = fields.Many2many('mailing.list',string=' Liste de diffusion')
    sender_phone = fields.Char("Numero de Telephone")
    #value2 = fields.Float(compute="_value_pc", store=True)
    message = fields.Text(string="Message")
    state = fields.Selection([('draft', 'Brouillon'),
                              ('valited', 'Validé'),
                              ('cancel', 'Annulé')
                              ], default='draft', string="Etat")

    def action_send_sms(self):

        # if not self.digital_signature:
        #     raise UserError(_("Veillez faire signer le destinataire du avant de valider la reception"))

        # Notification SMS a  l'expediteur
        api_key = 'b0l5cGl6TE5JZmt6ZkdIZEZsTUQ='
        url = 'https://app.techsoft-web-agency.com/sms/api'
        senderID = 'LeadersCorp'
        message = str(self.message)
        for contact in self.contact_list_ids:
            destination = str(contact.email)
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

    def action_view_mailing_contacts(self):
        """Show the mailing contacts who are in a mailing list selected for this mailing."""
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('mass_mailing.action_view_mass_mailing_contacts')
        if self.contact_list_ids:
            action['context'] = {
                'default_mailing_list_ids': self.contact_list_ids[0].ids,
                'default_subscription_list_ids': [(0, 0, {'list_id': self.contact_list_ids[0].id})],
            }
        action['domain'] = [('list_ids', 'in', self.contact_list_ids.ids)]
        return action