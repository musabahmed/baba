# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################

import time

from openerp.osv import fields, osv, orm

class social_insurrance_report(osv.osv_memory):
    
    def _get_months(self, cr, uid, context):
        return [(n, n) for n in range(1, 13)]
    
    _name = 'social.insurrance'
    
    _description = 'info about the monthly paid amount for the social insurance'
    
    _columns = {
   	    'scale_ids': fields.many2many('hr.salary.scale','insu_scale_rel','parent_id','child_id', 'Salary Scale',required=True),
   	    'company_ids': fields.many2many('res.company','insu_com_rel','insu_id','com_id', 'Company',required=True),		
    	'year' :fields.integer("Year" ,required=True), 
        'month' :fields.selection(_get_months,"Month",required=True), 
        'insurance_id':fields.many2one('hr.allowance.deduction', 'Insurance',required=True,domain="[('name_type','=','deduct')]"),
   	    'dept_ids': fields.many2many('hr.department','insu_dept_rel','insu_id','dept_id', 'Departmet',required=False),		
    }
    
    def _get_companies(self, cr, uid, context=None): 
        return [self.pool.get('res.users').browse(cr,uid,uid).company_id.id]

    def _get_scale_ids(self, cr, uid, context=None): 
        return self.pool.get('hr.salary.scale').search(cr,uid,[])

    _defaults ={
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
        'company_ids': _get_companies,
        'scale_ids': _get_scale_ids,
    }
 
 
    def print_report(self, cr, uid, ids, context={}):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'hr.payroll.main.archive',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'social.insurrance.webkit',
            'datas': datas,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
