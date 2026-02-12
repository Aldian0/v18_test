from odoo import models, fields, api
from odoo.exceptions import UserError

# 1. BASE CLASS
class ShipmentBase(models.Model):
    _name = 'shipment.base'
    _description = 'Shipment Base'

    distance_km = fields.Integer(string='Jarak (KM)', required=True, default=0)

    def calculate_base_cost(self):
        """Mengembalikan Rp 5.000 per KM"""
        return self.distance_km * 5000


# 2. STANDARD SHIPMENT
# Mewarisi ShipmentBase (Class Python), bukan models.Model
class StandardShipment(ShipmentBase): 
    _name = 'shipment.standard'
    _inherit = 'shipment.base'
    _description = 'Standard Shipment'

    handling_fee = fields.Integer(string='Handling Fee', default=20000, readonly=True)

    def calculate_total_cost(self):
        # Panggil method dari parent (ShipmentBase)
        base_cost = self.calculate_base_cost() 
        return base_cost + self.handling_fee


# 3. FRAGILE GOODS SHIPMENT
# Mewarisi StandardShipment (Class Python)
class FragileGoodsShipment(StandardShipment):
    _name = 'shipment.fragile'
    _inherit = 'shipment.standard'
    _description = 'Fragile Goods Shipment'
    _rec_name = 'name'

    name = fields.Char(string='No. Pengiriman', required=True, copy=False, default='New')
    insurance_cost = fields.Float(string='Insurance (10%)', compute='_compute_cost')
    total_cost = fields.Float(string='Total Cost', compute='_compute_cost')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'shipment.fragile'
            ) or 'New'
        return super().create(vals)

    def calculate_total_cost(self):
        # Override: Panggil method dari parent (StandardShipment)
        # super() di sini akan bekerja karena kita melakukan Python Inheritance
        standard_cost = super().calculate_total_cost() 
        return standard_cost + (standard_cost * 0.10)

    @api.depends('distance_km')
    def _compute_cost(self):
        for rec in self:
            rec.total_cost = rec.calculate_total_cost()
            rec.insurance_cost = rec.total_cost - (rec.calculate_base_cost() + 20000)


# 4. PRIORITY SHIPMENT
# Mewarisi StandardShipment (Class Python)
class PriorityShipment(StandardShipment):
    _name = 'shipment.priority'
    _inherit = 'shipment.standard'
    _description = 'Priority Shipment'
    _rec_name = 'name'

    name = fields.Char(string='No. Pengiriman', required=True, copy=False, default='New')
    priority_fee = fields.Integer(string='Priority Fee', default=50000, readonly=True)
    total_cost = fields.Float(string='Total Cost', compute='_compute_cost')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'shipment.priority'
            ) or 'New'
        return super().create(vals)

    def calculate_total_cost(self):
        # Override: Panggil method dari parent (StandardShipment)
        return super().calculate_total_cost() + self.priority_fee

    @api.depends('distance_km')
    def _compute_cost(self):
        for rec in self:
            rec.total_cost = rec.calculate_total_cost()


# 5. TEST GRAND TOTAL (REAL RECORD VERSION)
class ShipmentGrandTotal(models.Model):
    _name = 'shipment.test.grandtotal'
    _description = 'Test Grand Total Shipment'
    _rec_name = 'fragile_id'
    
    # name = fields.Char(string='No. Pengiriman', required=True, copy=False, default='New')

    fragile_id = fields.Many2one('shipment.fragile', string="Fragile Shipment")
    priority_id = fields.Many2one('shipment.priority', string="Priority Shipment")

    fragile_total = fields.Float(string="Fragile Cost", compute="_compute_totals")
    priority_total = fields.Float(string="Priority Cost", compute="_compute_totals")

    grand_total = fields.Float(string="Grand Total", compute="_compute_totals", store=True)

    @api.depends('fragile_id.distance_km', 'priority_id.distance_km')
    def _compute_totals(self):
        for rec in self:
            fragile_cost = 0
            priority_cost = 0

            if rec.fragile_id:
                fragile_cost = rec.fragile_id.calculate_total_cost()

            if rec.priority_id:
                priority_cost = rec.priority_id.calculate_total_cost()

            rec.fragile_total = fragile_cost
            rec.priority_total = priority_cost
            rec.grand_total = fragile_cost + priority_cost