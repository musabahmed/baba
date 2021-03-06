# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm
from openerp import tools
#----------------------------------------------------------
# Stock Location (Inherit)
#----------------------------------------------------------
class stock_location(osv.osv):
    _inherit = "stock.location"
    _columns = {
        'chained_picking_type': fields.selection([('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal'),
                                                  ('quality', 'Quality')], 'Shipping Type', help="Shipping Type of the Picking List that will contain the chained move (leave empty to automatically detect the type based on the source and destination locations)."),
    }

    def picking_type_get(self, cr, uid, from_location, to_location, context=None):
        """
        Gets type of picking.

        @param from_location: Source location
        @param to_location: Destination location
        @return: Location type
        """
        if context==None: context={}
        result = super(stock_location, self).picking_type_get(cr, uid, from_location, to_location, context=context)
        if (from_location.usage == 'supplier') and (to_location.usage == 'supplier'):
            result = 'quality'
        if context.has_key('type') and context['type'] == 'quality':
            result = 'quality'
        return result
   

#----------------------------------------------------------
# Stock Picking (Inherit)
#----------------------------------------------------------
class stock_picking(osv.osv):

    def create(self, cr, user, vals, context=None):
        """
        override to add the sequence of the quality
     
        @returns: String of New sequense value
        """
        if context==None: context={}
        if context.has_key('type') and context['type'] =='quality': 
            seq_obj_name = 'stock.picking.quality'
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(stock_picking, self).create(cr, user, vals, context)
        return new_id


    _inherit = "stock.picking"
    _columns = {
        'type': fields.selection([('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal'),
                                  ('quality', 'Quality')], 'Shipping Type', required=True, select=True,
                                  help="Shipping type specify, goods coming in or going out."),

    }
  

#----------------------------------------------------------
# Purchase Order (Inherit)
#----------------------------------------------------------
class purchase_order(osv.osv):

#FIXME: Depend on purchase
#TODO : inherit to update prepare_order_picking function 
    _inherit = "purchase.order"

    def _default_stock_location(self, cr, uid, context=None):
        try:
            location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock_quality', 'stock_location_quality')
            with tools.mute_logger('openerp.osv.orm'):
                self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
        except (orm.except_orm, ValueError):
            location_id = False
        return location_id

    _defaults = {
        'location_id': _default_stock_location,
    }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """
        Update the dict of values to create the new picking for a
        purchase.order

        @param order : order_id
        @return: dictionary of values (name, type) to be updated
        """
        res = super(purchase_order, self)._prepare_order_picking(cr, uid, order, context=context)
        res.update({ 
            'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.quality'),
            'type': 'quality',
            })
        return res

    def move_lines_get(self, cr, uid, ids, *args):
        res = []
        for order in self.browse(cr, uid, ids, context={}):
            if order.picking_ids:
                for pick in order.picking_ids:
                    res += [x.id for x in pick.move_lines]
        return res

    def onchange_dest_address_id(self, cr, uid, ids, address_id):
        if not address_id:
            return {}
        return {'value':{'warehouse_id': False}}

    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id):
        if not warehouse_id:
            return {}
        warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id)
        return {'value':{'dest_address_id': False}}

    def test_done(self, cr, uid, ids, context=None):
        """ Test whether the incoming shipments are done or not.
        @return: True or False
        """
        ok = True
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                if line.move_ids:
                    for move in line.move_ids:
                        if move.state !='done':
                            return False
        return ok

    def test_cancel(self, cr, uid, ids, context=None):
        """ Test whether the incoming shipments are canceled or not.
        @return: True or False
        """
        for order in self.browse(cr, uid, ids, context=context):
            for pick in order.picking_ids:
                for move in pick.move_lines:
                    if move.state not in ('cancel',):
                        return False
        return True

class stock_move(osv.osv):

#FIXME: Depend on purchase
#TODO : inherit to update prepare_chained_picking function 

    _inherit = "stock.move"

    def _default_move_type(self, cr, uid, context={}):
        """ 
        Gets default type of move

        @return: type
        """
        type = super(stock_move, self)._default_move_type(cr, uid, context=context)
        picking_type = context.get('picking_type')
        if picking_type == 'quality':
            type = 'quality'
        return type

    _columns = {
        'type': fields.related('picking_id', 'type', type='selection', selection=[('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal'),('quality', 'Quality')], string='Shipping Type'), 
         }
    _defaults = {
        'type': _default_move_type,
        }

    def _prepare_chained_picking(self, cr, uid, picking_name, picking, picking_type, moves_todo, context=None):
        """
        Update the dict of values to create the chained picking for a
        purchase.order

        @param str picking_name: desired new picking name
        @param browse_record picking: source picking (being chained to)
        @param str picking_type: desired new picking type
        @param  moves_todo: specification of the stock moves to be later included in this
        picking, in the form:[[move, (dest_location, auto_packing, chained_delay, chained_journal,
        chained_company_id, chained_picking_type)],...]
        See also :meth:`stock_location.chained_location_get`.
        @return: dictionary of values to be updated
        """
        res = super(stock_move, self)._prepare_chained_picking(cr, uid, picking_name, picking, picking_type, moves_todo, context=context)
        res.update({'invoice_state': picking.invoice_state })
        if picking.purchase_id:
           res.update({'purchase_id': picking.purchase_id.id })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
