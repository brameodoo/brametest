# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import tagged
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from .common import SuCashForecastTestCommon


@tagged('post_install', '-at_install')
class TestCreateUpdateCashForecastWizard(SuCashForecastTestCommon):
    """Test cases for create.update.cash.forecast wizard"""

    def test_wizard_creation(self):
        """Test basic wizard creation"""
        wizard = self.env['create.update.cash.forecast'].create({
            'period_id': self.period_jan.id,
            'calculate': 'forecast',
            'company_id': self.company.id,
            'calculated_base_on': 'real',
        })
        
        self.assertEqual(wizard.period_id, self.period_jan)
        self.assertEqual(wizard.calculate, 'forecast')
        self.assertEqual(wizard.company_id, self.company)
        self.assertEqual(wizard.calculated_base_on, 'real')

    def test_wizard_period_domain_computation_forecast(self):
        """Test period domain computation for forecast calculation"""
        wizard = self.env['create.update.cash.forecast'].create({
            'calculate': 'forecast',
            'company_id': self.company.id,
        })
        
        wizard._compute_period_domain()
        
        # Should include future periods
        self.assertIn(self.period_feb, wizard.period_domain)
        self.assertIn(self.period_mar, wizard.period_domain)

    def test_wizard_period_domain_computation_real(self):
        """Test period domain computation for real value calculation"""
        # Set current period to past
        self.period_jan.start_date = date.today() - timedelta(days=10)
        self.period_jan.end_date = date.today() - timedelta(days=1)
        
        wizard = self.env['create.update.cash.forecast'].create({
            'calculate': 'real',
            'company_id': self.company.id,
        })
        
        wizard._compute_period_domain()
        
        # Should include past periods
        self.assertIn(self.period_jan, wizard.period_domain)

    def test_wizard_prepare_create_manual_cash_forecast(self):
        """Test prepare create manual cash forecast method"""
        wizard = self.env['create.update.cash.forecast'].create({
            'calculated_base_on': 'real',
            'company_id': self.company.id,
        })
        
        forecast_vals = wizard.prepare_create_manual_cash_forecast(
            self.forecast_type_income, 
            self.period_jan
        )
        
        self.assertEqual(forecast_vals['name'], self.forecast_type_income.name)
        self.assertEqual(forecast_vals['forecast_type'], self.forecast_type_income.type)
        self.assertEqual(forecast_vals['company_id'], self.forecast_type_income.company_id.id)
        self.assertEqual(forecast_vals['forecast_period_id'], self.period_jan.id)
        self.assertEqual(forecast_vals['forecast_type_id'], self.forecast_type_income.id)
        self.assertEqual(forecast_vals['forecast_date'], date.today())

    def test_wizard_create_manual_cash_forecast(self):
        """Test create manual cash forecast method"""
        wizard = self.env['create.update.cash.forecast'].create({
            'calculated_base_on': 'real',
            'company_id': self.company.id,
            'cash_forecast_type_ids': [(6, 0, [self.forecast_type_income.id])],
        })
        
        # Create some move lines for calculation
        self.create_test_move_line(self.account_income, -1000.0, date(2024, 1, 15))
        
        result = wizard.create_manual_cash_forecast(self.period_jan)
        self.assertTrue(result)
        
        # Check that forecast was created
        forecast = self.env['setu.cash.forecast'].search([
            ('forecast_type_id', '=', self.forecast_type_income.id),
            ('forecast_period_id', '=', self.period_jan.id),
            ('company_id', '=', self.company.id),
        ])
        
        self.assertTrue(forecast)

    def test_wizard_create_manual_cash_forecast_without_types(self):
        """Test create manual cash forecast without specifying types"""
        wizard = self.env['create.update.cash.forecast'].create({
            'calculated_base_on': 'real',
            'company_id': self.company.id,
        })
        
        result = wizard.create_manual_cash_forecast(self.period_jan)
        self.assertTrue(result)
        
        # Should create forecasts for all applicable types
        forecasts = self.env['setu.cash.forecast'].search([
            ('forecast_period_id', '=', self.period_jan.id),
            ('company_id', '=', self.company.id),
        ])
        
        self.assertGreater(len(forecasts), 0)

    def test_wizard_create_manual_cash_forecast_with_dependencies(self):
        """Test create manual cash forecast with dependent forecast types"""
        # Create dependent forecast type
        dependent_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Dependent Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        # Set dependency
        self.forecast_type_income.dep_forecast_ids = [(6, 0, [dependent_type.id])]
        
        wizard = self.env['create.update.cash.forecast'].create({
            'calculated_base_on': 'real',
            'company_id': self.company.id,
            'cash_forecast_type_ids': [(6, 0, [self.forecast_type_income.id])],
        })
        
        result = wizard.create_manual_cash_forecast(self.period_jan)
        self.assertTrue(result)
        
        # Should create forecasts for both main and dependent types
        main_forecast = self.env['setu.cash.forecast'].search([
            ('forecast_type_id', '=', self.forecast_type_income.id),
            ('forecast_period_id', '=', self.period_jan.id),
        ])
        
        dep_forecast = self.env['setu.cash.forecast'].search([
            ('forecast_type_id', '=', dependent_type.id),
            ('forecast_period_id', '=', self.period_jan.id),
        ])
        
        self.assertTrue(main_forecast)
        self.assertTrue(dep_forecast)

    def test_wizard_create_cash_forecast_validation(self):
        """Test create cash forecast validation"""
        wizard = self.env['create.update.cash.forecast'].create({
            'period_id': self.period_jan.id,
            'calculate': 'forecast',
            'company_id': self.company.id,
        })
        
        # Set period to past to trigger validation error
        self.period_jan.start_date = date.today() - timedelta(days=10)
        self.period_jan.end_date = date.today() - timedelta(days=1)
        
        with self.assertRaises(ValidationError):
            wizard.create_cash_forecast()

    def test_wizard_create_cash_forecast_success(self):
        """Test successful create cash forecast"""
        wizard = self.env['create.update.cash.forecast'].create({
            'period_id': self.period_feb.id,  # Future period
            'calculate': 'forecast',
            'company_id': self.company.id,
        })
        
        result = wizard.create_cash_forecast()
        self.assertTrue(result)
        
        # Check that forecasts were created
        forecasts = self.env['setu.cash.forecast'].search([
            ('forecast_period_id', '=', self.period_feb.id),
            ('company_id', '=', self.company.id),
        ])
        
        self.assertGreater(len(forecasts), 0)

    def test_wizard_calculate_value_forecast(self):
        """Test calculate value method for forecast calculation"""
        wizard = self.env['create.update.cash.forecast'].create({
            'period_id': self.period_feb.id,
            'calculate': 'forecast',
            'company_id': self.company.id,
        })
        
        action = wizard.calculate_value()
        
        self.assertEqual(action['res_model'], 'setu.cash.forecast')
        self.assertEqual(action['view_mode'], 'pivot,list,form')
        self.assertEqual(action['type'], 'ir.actions.act_window')

    def test_wizard_calculate_value_real(self):
        """Test calculate value method for real value calculation"""
        # Set period to past
        self.period_jan.start_date = date.today() - timedelta(days=10)
        self.period_jan.end_date = date.today() - timedelta(days=1)
        
        wizard = self.env['create.update.cash.forecast'].create({
            'period_id': self.period_jan.id,
            'calculate': 'real',
            'company_id': self.company.id,
        })
        
        action = wizard.calculate_value()
        
        self.assertEqual(action['res_model'], 'setu.cash.forecast')
        self.assertEqual(action['view_mode'], 'pivot,list,form')
        self.assertEqual(action['type'], 'ir.actions.act_window')

    def test_wizard_calculate_value_real_validation(self):
        """Test calculate value method validation for real calculation"""
        wizard = self.env['create.update.cash.forecast'].create({
            'period_id': self.period_feb.id,  # Future period
            'calculate': 'real',
            'company_id': self.company.id,
        })
        
        with self.assertRaises(ValidationError):
            wizard.calculate_value()

    def test_wizard_update_cash_forecast(self):
        """Test update cash forecast method"""
        wizard = self.env['create.update.cash.forecast'].create({
            'period_id': self.period_jan.id,
            'calculate': 'forecast',
            'company_id': self.company.id,
        })
        
        context = {
            'cash_forecast_type_ids': [self.forecast_type_income.id],
            'period_id': self.period_jan.id,
        }
        
        action = wizard.with_context(context).update_cash_forecast()
        
        self.assertEqual(action['res_model'], 'create.update.cash.forecast')
        self.assertEqual(action['type'], 'ir.actions.act_window')

    def test_wizard_help_text(self):
        """Test wizard help text"""
        wizard = self.env['create.update.cash.forecast'].create({
            'company_id': self.company.id,
        })
        
        self.assertIn('NOTE:', wizard.help_for_wizard)
        self.assertIn('Cash Forecast', wizard.help_for_wizard)

    def test_wizard_company_isolation(self):
        """Test that wizard respects company isolation"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create wizard for other company
        other_wizard = self.env['create.update.cash.forecast'].create({
            'period_id': self.period_jan.id,
            'calculate': 'forecast',
            'company_id': other_company.id,
        })
        
        self.assertEqual(other_wizard.company_id, other_company)

    def test_wizard_calculated_base_on_options(self):
        """Test calculated_base_on field options"""
        # Test real option
        wizard_real = self.env['create.update.cash.forecast'].create({
            'calculated_base_on': 'real',
            'company_id': self.company.id,
        })
        self.assertEqual(wizard_real.calculated_base_on, 'real')
        
        # Test demo option
        wizard_demo = self.env['create.update.cash.forecast'].create({
            'calculated_base_on': 'demo',
            'company_id': self.company.id,
        })
        self.assertEqual(wizard_demo.calculated_base_on, 'demo')

    def test_wizard_cash_forecast_type_ids_relationship(self):
        """Test cash forecast type ids relationship"""
        wizard = self.env['create.update.cash.forecast'].create({
            'cash_forecast_type_ids': [(6, 0, [self.forecast_type_income.id, self.forecast_type_expense.id])],
            'company_id': self.company.id,
        })
        
        self.assertIn(self.forecast_type_income, wizard.cash_forecast_type_ids)
        self.assertIn(self.forecast_type_expense, wizard.cash_forecast_type_ids)

    def test_wizard_calculate_options(self):
        """Test calculate field options"""
        # Test forecast option
        wizard_forecast = self.env['create.update.cash.forecast'].create({
            'calculate': 'forecast',
            'company_id': self.company.id,
        })
        self.assertEqual(wizard_forecast.calculate, 'forecast')
        
        # Test real option
        wizard_real = self.env['create.update.cash.forecast'].create({
            'calculate': 'real',
            'company_id': self.company.id,
        })
        self.assertEqual(wizard_real.calculate, 'real')

    def test_wizard_period_domain_empty(self):
        """Test period domain when no calculate option is selected"""
        wizard = self.env['create.update.cash.forecast'].create({
            'company_id': self.company.id,
        })
        
        wizard._compute_period_domain()
        
        # Should be empty when no calculate option is selected
        self.assertEqual(len(wizard.period_domain), 0)

    def test_wizard_period_domain_with_company_filter(self):
        """Test period domain with company filter"""
        # Create another company with its own periods
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        other_fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Other Fiscal Year',
            'company_id': other_company.id,
            'date_from': date(2024, 1, 1),
            'date_to': date(2024, 12, 31),
            'period_interval': 'months',
        })
        
        other_period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Other Period',
            'fiscal_id': other_fiscal_year.id,
            'start_date': date(2024, 4, 1),
            'end_date': date(2024, 4, 30),
            'company_id': other_company.id,
        })
        
        wizard = self.env['create.update.cash.forecast'].create({
            'calculate': 'forecast',
            'company_id': self.company.id,
        })
        
        wizard._compute_period_domain()
        
        # Should only include periods from the specified company
        self.assertNotIn(other_period, wizard.period_domain)
        self.assertIn(self.period_feb, wizard.period_domain)

    def test_wizard_create_manual_cash_forecast_update_existing(self):
        """Test create manual cash forecast updates existing records"""
        # Create existing forecast
        existing_forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=1000.0
        )
        
        wizard = self.env['create.update.cash.forecast'].create({
            'calculated_base_on': 'real',
            'company_id': self.company.id,
            'cash_forecast_type_ids': [(6, 0, [self.forecast_type_income.id])],
            'period_id': self.period_jan.id,
        })
        
        # Create some move lines for new calculation
        self.create_test_move_line(self.account_income, -2000.0, date(2024, 1, 15))
        
        result = wizard.create_manual_cash_forecast(self.period_jan)
        self.assertTrue(result)
        
        # Check that existing forecast was updated
        existing_forecast.refresh()
        self.assertNotEqual(existing_forecast.forecast_value, 1000.0)
