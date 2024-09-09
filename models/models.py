from odoo import models, fields, api, tools, _
from datetime import datetime, timedelta
import qrcode
import base64
from io import BytesIO

# class ProductProduct(models.Model):
#     _inherit = 'product.product'

#     warranty_type = fields.Selection(
#         related="warranty_rule_id.description", readonly=True)
#     warranty_rule_id = fields.Many2one(
#         'warranty.rule', string='Warranty rules')

#     warranty_count = fields.Integer(
#         related="warranty_rule_id.warranty_count", readonly=True)
#     warranty_duration = fields.Selection(
#         related="warranty_rule_id.warranty_duration", readonly=True)
#     warranty_serial = fields.Char(
#         string='Warranty Serial', compute='_compute_warranty_serial', store=True, default=lambda self: _('New'))

#     @api.depends('warranty_rule_id')
#     def _compute_warranty_serial(self):
#         for product in self:
#             if product.warranty_rule_id:
#                 product.warranty_serial = product.create_serial()

#             else:
#                 product.warranty_serial = False

#     def create_serial(self):
#         for product in self:
#             return self.env['ir.sequence'].next_by_code('warranty.serial') or _('New')

# order_partner_id = fields.Many2one('res.partner', string='Order Partner')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    warranty_type = fields.Selection(
        related="product_tmpl_id.warranty_type", readonly=True)
    warranty_rule_id = fields.Many2one(
        'warranty.rule', string='Warranty rules')

    warranty_count = fields.Integer(
        related="product_tmpl_id.warranty_count", readonly=True)
    warranty_duration = fields.Selection(
        related="product_tmpl_id.warranty_duration", readonly=True)

    has_warranty_rule = fields.Boolean(
        string='Has Warranty Rule',
        compute='_compute_has_warranty_rule',
        store=True
    )

    @api.depends('warranty_rule_id')
    def _compute_has_warranty_rule(self):
        for product in self:
            product.has_warranty_rule = bool(product.warranty_rule_id)

    @api.onchange('product_tmpl_id.warranty_type', 'product_tmpl_id.warranty_rule_id',
                  'product_tmpl_id.warranty_count', 'product_tmpl_id.warranty_duration')
    def _onchange_warranty_info(self):
        for variant in self:
            variant.warranty_type = variant.product_tmpl_id.warranty_type
            variant.warranty_rule_id = variant.product_tmpl_id.warranty_rule_id
            variant.warranty_count = variant.product_tmpl_id.warranty_count
            variant.warranty_duration = variant.product_tmpl_id.warranty_duration


class ProductProduct(models.Model):
    _inherit = 'product.template'

    warranty_type = fields.Selection(
        related="warranty_rule_id.description", readonly=True)
    warranty_rule_id = fields.Many2one(
        'warranty.rule', string='Warranty rules')

    warranty_count = fields.Integer(
        related="warranty_rule_id.warranty_count", readonly=True)
    warranty_duration = fields.Selection(
        related="warranty_rule_id.warranty_duration", readonly=True)

    has_warranty_rule = fields.Boolean(
        string='Has Warranty Rule',
        compute='_compute_has_warranty_rule',
        store=True
    )

    @api.depends('warranty_rule_id')
    def _compute_has_warranty_rule(self):
        for product in self:
            product.has_warranty_rule = bool(product.warranty_rule_id)


class Warrantyrule(models.Model):
    _name = 'warranty.rule'
    _inherit = 'mail.thread'

    name = fields.Char(string="Warranty Name")
    description = fields.Selection([
        ('warranty', 'Warranty'),
        ('guarantee', 'Guarantee')
    ], string='Warranty Type', store="true", tracking=True)
    warranty_count = fields.Integer(String="Day Count", tracking=True)
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
        w_product__ids = self.env['product.product'].search(
            [('warranty_rule_id', '=', self.id)]).ids
        self.w_product__ids = w_product__ids
        for rule in self:
            rule.w_products_count = len(rule.w_product__ids)

    @api.depends('w_product__ids')
    def _get_products_count(self):
        for rule in self:
            rule.w_products_count = len(self.env['product.product'].search(
                [('warranty_rule_id', '=', rule.id)]).ids)


class feedback(models.Model):
    _name = 'warranty.feedback'
    _description = 'give us a feedback'

    name = fields.Char(string='Name')
    feedback = fields.Text(string='Feedback')


class CustomStockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = 'date_done desc'
    warranty_status = fields.Selection([
        ('expired', 'Expired'),
        ('available', 'Available')
    ], string="Status", store=True, readonly=True)
    loc_type = fields.Selection(
        related='location_dest_id.usage', string="Location Type")
    phone = fields.Char(related="partner_id.phone", string="Phone")
    email = fields.Char(related="partner_id.email", string="Email")
    warranty_end_date = fields.Date(
        string='Expiry Date', readonly=True)
    warranty_product = fields.Boolean(
        string="Warranty Product", default=False, readonly=True)
    warranty_serial = fields.Char(
        string='Serial', store=True, readonly=True, default=lambda self: _('New'))
    pick_type = fields.Selection(
        related="picking_type_id.code", string="Picking Type")

    @api.depends('product_id.product_tmpl_id.warranty_rule_id')
    def _compute_warranty_serial(self):
        for picking in self:
            if picking.product_id.product_tmpl_id.warranty_rule_id:
                picking.warranty_serial = picking.create_serial()
                print("serial generated ", picking.warranty_serial)
            else:
                picking.warranty_serial = False

    def create_serial(self):
        return self.env['ir.sequence'].next_by_code('warranty.serial') or _('New')

    def _action_done(self):
        # Call the original _action_done method from stock.picking
        super(CustomStockPicking, self)._action_done()

        # Compute warranty dates after _action_done is executed
        if self.picking_type_id.code == 'outgoing':
            self._compute_warranty_dates()
            self._compute_warranty_serial()
            print("Ghusgaya")
        # Any additional logic you want to add after _action_done

        return True

    @api.depends('date_done', 'product_id.product_tmpl_id.warranty_rule_id', 'product_id.product_tmpl_id.warranty_rule_id.warranty_count')
    def _compute_warranty_dates(self):
        for picking in self:
            print("Date Done", picking.date_done)
            print("pro warranty .product_id.product_tmpl_id.warranty_rule_id-------",
                  picking.product_id.product_tmpl_id.warranty_rule_id)
            print("pro warranty count-------",
                  picking.product_id.product_tmpl_id.warranty_rule_id.warranty_count)
            if picking.date_done and picking.product_id.product_tmpl_id.warranty_rule_id:
                warranty_dur = picking.product_id.product_tmpl_id.warranty_rule_id.warranty_count * 30
                warranty_end_date = picking.date_done + \
                    timedelta(days=warranty_dur)
                # Ensure to store only date, not datetime
                picking.warranty_end_date = warranty_end_date.date()
                picking.warranty_product = True
                print("picking.warranty_end_date", picking.warranty_end_date)
                print("picking.warranty_product", picking.warranty_product)

                if picking.warranty_end_date > datetime.now().date():
                    picking.warranty_status = 'available'
                else:
                    picking.warranty_status = 'expired'

            else:
                picking.warranty_end_date = False
                picking.warranty_status = False
                picking.warranty_product = False

    def action_open_support_ticket(self):
        action = {
            'name': 'Warranty Claim',
            'type': 'ir.actions.act_window',
            'res_model': 'support.ticket',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_catagory': "Warranty Claim",
                'default_phone': self.partner_id.phone,
                'default_email': self.partner_id.email,
                'default_product_id': self.product_id.id,
                'default_sku': self.product_id.default_code,
                'default_warranty_type': self.product_id.product_tmpl_id.warranty_type,
                'default_warranty_rule_id': self.product_id.product_tmpl_id.warranty_rule_id.name,
                'default_warranty_end_date': self.warranty_end_date,
                'default_warranty_status': self.warranty_status,
                'default_warranty_serial': self.warranty_serial,
                'default_warranty_product': self.warranty_product,
                'default_so_no': self.origin,
                'default_date_done': self.date_done,
                'default_qty': 1,
                'default_name': tools.ustr("%s's Claim") % self.partner_id.name
            }
        }
        return action


class SupportTicketInherito(models.Model):
    _inherit = 'support.ticket'

    product_id = fields.Many2one(
        'product.product', string='Name of the Product', domain=[('sale_ok', '=', True)])
    sku = fields.Char(related="product_id.default_code", string="SKU ")
    qty = fields.Integer(String="Quantity")
    warranty_type = fields.Selection(
        related="product_id.product_tmpl_id.warranty_type", readonly=True, string="Warranty Type")
    warranty_rule_id = fields.Char(
        related="product_id.product_tmpl_id.warranty_rule_id.name", string='Warranty Rule')
    warranty_status = fields.Selection([
        ('expired', 'Expired'),
        ('available', 'Available')
    ], string="Warranty Status", store=True)
    warranty_end_date = fields.Date(
        string='Warranty End Date', readonly=True)
    warranty_product = fields.Boolean(string="Warranty Product")
    warranty_serial = fields.Char(
        string='Warranty Serial', store=True)
    so_no = fields.Char(string='SO Number')
    date_done = fields.Datetime(string="Delivered Date")
    is_rma = fields.Boolean(string="Is RMA")

    def action_create_rma(self):

        sale_order_line_values = {
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'product_uom_qty': self.qty or 1,  # You can adjust the quantity as needed
            'price_unit': 0,
            'price_subtotal': 0,
            'price_total': 0,
            # 'sequence2': 1,
        }
        action = {
            'name': 'Create RMA',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_product_id': self.product_id.id,
                'default_so_no': self.so_no,
                'default_is_rma': True,
                'default_order_line': [(0, 0, sale_order_line_values)],
            }
        }
        self.is_rma = True

        return action

    is_claim = fields.Boolean(string="Claim Warranty")
    name = fields.Char('Subject', required=True,
        compute='_compute_name', readonly=False, store=True)
    
    @api.depends('partner_id')
    def _compute_name(self):
        for lead in self:
            if not lead.name and lead.partner_id and lead.partner_id.name and lead.is_claim:
                lead.name = _("%s's Claim") % lead.partner_id.name 


    qr_code = fields.Binary(
        string="QR Code", compute='_generate_qr_code', store=True)

    @api.depends('name', 'warranty_status','warranty_type','warranty_product' ,'warranty_end_date', 'warranty_serial')
    def _generate_qr_code(self):
        for record in self:
            data = f"Name: {record.product_id}\nRef: {record.sku}\nStatus: {record.warranty_status}\nPurchase Date: {record.date_done}\nWarranty End Date: {record.warranty_end_date}\nSerial: {record.warranty_serial}"
            print("QR Code Information", data)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=8,
                border=3,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((100, 100))
            tmp = BytesIO()
            img.save(tmp, format="PNG")
            qr_img = base64.b64encode(tmp.getvalue())
            print("QR Image Data", qr_img)
            record.qr_code = qr_img
            
            
            
class SaleORder(models.Model):
    _inherit = 'sale.order'

    is_rma = fields.Boolean(string="Is RMA")
    so_no = fields.Char(string="Backorder No.")
    past_record = fields.Boolean(string='Past Record')

    def _prepare_confirmation_values(self):
        """ Prepare the sales order confirmation values.

        Note: self can contain multiple records.

        :return: Sales Order confirmation values
        :rtype: dict
        """
        return {
            'state': 'sale',
            'date_order': self.date_order if self.past_record else fields.Datetime.now()
        }
