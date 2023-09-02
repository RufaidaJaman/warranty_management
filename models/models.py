from odoo import models, fields, api,_
from datetime import datetime, timedelta


class ProductProduct(models.Model):
    _inherit = 'product.product'

    warranty_type = fields.Selection( related="warranty_rule_id.description", readonly=True)
    warranty_rule_id = fields.Many2one('warranty.rule', string='Warranty rules')

    warranty_count = fields.Integer( related="warranty_rule_id.warranty_count", readonly=True)
    warranty_duration = fields.Selection( related="warranty_rule_id.warranty_duration", readonly=True)
    warranty_serial = fields.Char(string='Warranty Serial', compute='_compute_warranty_serial', store=True,default=lambda self: _('New'))
    

    @api.depends('warranty_rule_id')
    def _compute_warranty_serial(self):
        for product in self:
            if product.warranty_rule_id:
                product.warranty_serial = product.create_serial()
                
            else:
                product.warranty_serial = False
                
    def create_serial(self):
        for product in self:
            return self.env['ir.sequence'].next_by_code('warranty.serial') or _('New')  
        

class ProductProduct(models.Model):
    _inherit = 'product.template'

    warranty_type = fields.Selection( related="warranty_rule_id.description", readonly=True)
    warranty_rule_id = fields.Many2one('warranty.rule', string='Warranty rules')

    warranty_count = fields.Integer( related="warranty_rule_id.warranty_count", readonly=True)
    warranty_duration = fields.Selection( related="warranty_rule_id.warranty_duration", readonly=True)
    warranty_serial = fields.Char(string='Warranty Serial', compute='_compute_warranty_serial', store=True,default=lambda self: _('New'))
    

    @api.depends('warranty_rule_id')
    def _compute_warranty_serial(self):
        for product in self:
            if product.warranty_rule_id:
                product.warranty_serial = product.create_serial()
                
            else:
                product.warranty_serial = False
                
    def create_serial(self):
        for product in self:
            return self.env['ir.sequence'].next_by_code('warranty.serial') or _('New')      
        
        
            
class Warrantyrule(models.Model):
    _name = 'warranty.rule'
    _inherit = 'mail.thread'
    
    name= fields.Char(string="Warranty Name")
    description=  fields.Selection([
        ('warranty', 'Warranty'),
        ('guarantee', 'Guarantee')
    ], string='Warranty Type', store="true" , tracking=True)
    warranty_count= fields.Integer(String="Day Count", tracking=True)
    warranty_duration = fields.Selection([
        ('months', 'Months')
    ], string='Warranty Duration', tracking=True)

    w_products_count = fields.Integer(
        string='Number of products',
        compute='_get_products_count',
        help='It shows the number of product counts'
    )
    w_product__ids = fields.Many2many(
        'product.product',
        string='Products',
        help="Add products for this rules")
    
    def get_products(self):
        w_product__ids = self.env['product.product'].search([('warranty_rule_id', '=', self.id)]).ids
        self.w_product__ids = w_product__ids
        for rule in self:
            rule.w_products_count = len(rule.w_product__ids)
    
    @api.depends('w_product__ids')
    def _get_products_count(self):
        for rule in self:
            rule.w_products_count = len(self.env['product.product'].search([('warranty_rule_id', '=', rule.id)]).ids)    
            
class WarrantyClaim(models.Model):
    _name = 'warranty.claim'
    _inherit = 'mail.thread'
    
    name = fields.Many2one('product.product','warranty_serial')
    pro_name = fields.Char( related="name.name", readonly=True)
    pro_type = fields.Selection( related="name.detailed_type", readonly=True)
    
    warranty_typec = fields.Selection( related="name.warranty_type", readonly=True)

    warranty_countc = fields.Integer( related="name.warranty_count", readonly=True)
    
    warranty_durationc = fields.Selection( related="name.warranty_duration", readonly=True)
    
    
class feedback(models.Model):
    _name = 'warranty.feedback'
    _description = 'give us a feedback'

    name = fields.Char(string='Name')
    feedback = fields.Text(string='Feedback')   


class StockPicking(models.Model):
    _name = 'productstock.picking'
    _inherit = 'stock.picking'
                
    warranty_status=fields.Selection([
        ('expired', 'Expired'),
        ('available', 'Available')
    ], string="Warranty Status")
    
    
    product_id = fields.Many2one('product.product', string='Product', required=True)
    phone = fields.Char(related="partner_id.phone", string="Phone")
    email = fields.Char(related="partner_id.email", string="Email")
    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=True, help="Date at which the transfer has been processed or cancelled.")
    
    warranty_end_date = fields.Date(string='Warranty End Date', compute="_compute_warranty_dates", store=True)
    
    serial_id = fields.Many2one('product.product', string='Product', required=True)
    
    stock_id = fields.Many2one('stock.lot')
    serial = fields.Char(related='stock_id.name', string='Serial')
    
    @api.depends('date_done', 'product_id.warranty_rule_id', 'product_id.warranty_rule_id.warranty_count')
    def _compute_warranty_dates(self):
        
        for picking in self:
            if picking.date_done and picking.product_id.warranty_rule_id:
                warranty_dur = picking.product_id.warranty_rule_id.warranty_count * 30
                warranty_end_date = picking.date_done + timedelta(days=warranty_dur)
                picking.warranty_end_date = warranty_end_date
                if picking.warranty_end_date >(datetime.now()).date():
                    picking.warranty_status='available'
                else:
                    picking.warranty_status='expired'
            else:
                picking.warranty_end_date = False
                
                
    


