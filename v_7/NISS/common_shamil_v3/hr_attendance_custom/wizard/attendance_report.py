# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
##############################################################################

from osv import osv, fields
from tools.translate import _

class print_attendance(osv.osv_memory):

    _name = 'print.attendance'

    _columns = {
        'lower_deps':fields.boolean(string="Include Lower Departments"),
        'deps':fields.many2many('hr.department','dep_attendance','atten_id','dep_id', 'Department'),
        'dfrom':fields.date('From' ,required=True),
        'dto':fields.date('To',required=True),
    }

    def print_report(self, cr, uid, ids, data, context=None):
        wiz_data =self.read(cr, uid, ids[0], context={})
        datas = {
            'ids': [],
            'model':'hr.employee',
            'form':wiz_data
                }
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'print.attendance',
                    'datas':datas
               }

 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
