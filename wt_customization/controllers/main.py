# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from datetime import datetime

class WtCustomization(http.Controller):
    
    @http.route("/host-site-partner-1",type="http",auth="public",website=True)
    def host_site_partner(self,**kwargs):
        return request.render("wt_customization.wt_customization")
    
    @http.route("/youth-appication",type="http",auth="public",website=True)
    def host_site_applications(self,**kwargs):
        return request.render("wt_customization.wt_youth_application")
    
    @http.route("/hr-issues",type="http",auth="public",website=True)
    def hr_issue(self,**kwargs):
        return request.render("wt_customization.wt_hr_issue")
    
    @http.route("/job-vacancies",type="http",auth="public",website=True)
    def job_vacancies(self,**kwargs):
        return request.render("wt_customization.wt_job_vacancies_page")

    @http.route("/create-leave", type="http", auth="public", website=True)
    def create_leaves(self,**kwargs):
        return request.render("wt_customization.wt_youth_leave_form")



    @http.route("/leave/form",type='http', auth='public', method=['POST'], website=True)
    def create_leave_from_portal(self, **kwargs):
        holiday_status_id = kwargs.get('holiday_status_id')
        leave_type = request.env['hr.leave.type'].sudo().browse(int(holiday_status_id))
        employee_id = kwargs.get('employee_id')
        employee = request.env['hr.employee'].sudo().browse(int(employee_id))
        date_from = False
        date_to = False
        duration = False
        if kwargs.get('date_from'):
            date_from = datetime.strptime(kwargs.get('date_from'), '%Y-%m-%d').date()
        if kwargs.get('date_to'):
            date_to = datetime.strptime(kwargs.get('date_to'), '%Y-%m-%d').date()
        if date_from and date_to:
            duration = (date_to - date_from).days + 1
        vals = {
            'holiday_status_id':leave_type.id,
            'date_from':date_from,
            'date_to':date_to,
            'request_date_from':date_from,
            'request_date_to':date_to,
            'employee_id':employee.id,
            'request_unit_half': True if kwargs.get('is_halfday') == 'on' else False,
            'request_date_from_period':kwargs.get('day_period'),
            'name':kwargs.get('description'),
            'number_of_days_display':duration,
            'number_of_days':duration
        }
        if kwargs.get('is_halfday') == 'on':
            vals.update({
                'date_from':datetime.strptime(kwargs.get('halfday_date'), '%Y-%m-%d').date(),
                'date_to':datetime.strptime(kwargs.get('halfday_date'), '%Y-%m-%d').date(),
                'request_date_from':datetime.strptime(kwargs.get('halfday_date'), '%Y-%m-%d').date(),
                'request_date_to':datetime.strptime(kwargs.get('halfday_date'), '%Y-%m-%d').date(),
                'number_of_days_display':0.5,
                'number_of_days':0.5
                })
        leaves = request.env['hr.leave'].sudo().create(vals)
        return request.redirect('/contactus-thank-you')

    
    @http.route("/get_states",type="json",auth="public")
    def get_state(self,**kwargs):
        country_id = kwargs.get("country_id")
        if country_id:
            country = request.env["res.country"].sudo().browse(country_id)
            if country:
                states = request.env["res.country.state"].sudo().search_read(domain=[("country_id","=",country.id)],fields=["id","name"])
                return  states
        
    @http.route("/get_host_type_partner",type="json",auth="public")
    def get_host_type_partner(self,**kwargs):
        youth_company_type = kwargs.get("youth_company_type")
        if youth_company_type:
            partners = request.env["res.partner"].sudo().search_read(domain=[("youth_company_type","=",youth_company_type)])
            return  partners
    
    @http.route("/resignations",type="http",auth="public",website=True)
    def get_resignation_page(self,**kwargs):
        return request.render("wt_customization.wt_resignation")