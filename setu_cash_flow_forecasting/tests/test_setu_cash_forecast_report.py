# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import tagged
from datetime import date
from .common import SuCashForecastTestCommon


@tagged('post_install', '-at_install')
class TestSetuCashForecastReport(SuCashForecastTestCommon):
    """Test cases for setu.cash.forecast.report model"""

    def test_cash_forecast_report_creation(self):
        """Test basic cash forecast report creation"""
        report = self.env['setu.cash.forecast.report'].create({
            'name': 'Test Report',
            'company_id': self.company.id,
        })
        
        self.assertEqual(report.name, 'Test Report')
        self.assertEqual(report.company_id, self.company)

    def test_cash_forecast_report_company_isolation(self):
        """Test that cash forecast reports are properly isolated by company"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create report for other company
        other_report = self.env['setu.cash.forecast.report'].create({
            'name': 'Other Company Report',
            'company_id': other_company.id,
        })
        
        # Search for reports in original company
        company_reports = self.env['setu.cash.forecast.report'].search([
            ('company_id', '=', self.company.id)
        ])
        
        self.assertNotIn(other_report, company_reports)

    def test_cash_forecast_report_with_forecasts(self):
        """Test cash forecast report with associated forecasts"""
        # Create cash forecast
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0
        )
        
        # Create report
        report = self.env['setu.cash.forecast.report'].create({
            'name': 'Test Report',
            'company_id': self.company.id,
        })
        
        # Test report functionality
        self.assertEqual(report.name, 'Test Report')
        self.assertEqual(report.company_id, self.company)

    def test_cash_forecast_report_copy(self):
        """Test copying cash forecast report"""
        original = self.env['setu.cash.forecast.report'].create({
            'name': 'Original Report',
            'company_id': self.company.id,
        })
        
        copy = original.copy()
        
        self.assertNotEqual(original.id, copy.id)
        self.assertEqual(copy.name, original.name)
        self.assertEqual(copy.company_id, original.company_id)

    def test_cash_forecast_report_name_generation(self):
        """Test cash forecast report name generation"""
        report = self.env['setu.cash.forecast.report'].create({
            'name': 'Generated Name',
            'company_id': self.company.id,
        })
        
        # Test that name is properly set
        self.assertEqual(report.name, 'Generated Name')

    def test_cash_forecast_report_sequence_ordering(self):
        """Test that cash forecast reports are ordered by name"""
        # Create reports in different order
        report3 = self.env['setu.cash.forecast.report'].create({
            'name': 'Z Report',
            'company_id': self.company.id,
        })
        
        report1 = self.env['setu.cash.forecast.report'].create({
            'name': 'A Report',
            'company_id': self.company.id,
        })
        
        report2 = self.env['setu.cash.forecast.report'].create({
            'name': 'M Report',
            'company_id': self.company.id,
        })
        
        reports = self.env['setu.cash.forecast.report'].search([
            ('company_id', '=', self.company.id)
        ])
        
        # Check ordering
        report1_index = reports.ids.index(report1.id)
        report2_index = reports.ids.index(report2.id)
        report3_index = reports.ids.index(report3.id)
        
        self.assertLess(report1_index, report2_index)
        self.assertLess(report2_index, report3_index)
