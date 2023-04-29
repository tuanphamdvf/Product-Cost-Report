from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ProductIsFinished(models.Model):
    _inherit = 'product.template'
    _description = 'product'

    is_finished = fields.Boolean(string="Finished goods")
    is_main_material = fields.Boolean(string="Main Material")
