# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class SuCashForecastTestCommon(TransactionCase):
    """Common test class for Cash Flow Forecasting module tests"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create test company
        cls.company = cls.env['res.company'].create({
            'name': 'Test Company',
            'currency_id': cls.env.ref('base.USD').id,
        })
        
        # Create test fiscal year
        cls.fiscal_year = cls.env['cash.forecast.fiscal.year'].create({
            'name': 'Test Fiscal Year 2024',
            'company_id': cls.company.id,
            'date_from': date(2024, 1, 1),
            'date_to': date(2024, 12, 31),
            'period_interval': 'months',
        })
        
        # Create test fiscal periods
        cls.period_jan = cls.env['cash.forecast.fiscal.period'].create({
            'name': 'January 2024',
            'fiscal_id': cls.fiscal_year.id,
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 1, 31),
            'company_id': cls.company.id,
        })
        
        cls.period_feb = cls.env['cash.forecast.fiscal.period'].create({
            'name': 'February 2024',
            'fiscal_id': cls.fiscal_year.id,
            'start_date': date(2024, 2, 1),
            'end_date': date(2024, 2, 29),
            'company_id': cls.company.id,
        })
        
        cls.period_mar = cls.env['cash.forecast.fiscal.period'].create({
            'name': 'March 2024',
            'fiscal_id': cls.fiscal_year.id,
            'start_date': date(2024, 3, 1),
            'end_date': date(2024, 3, 31),
            'company_id': cls.company.id,
        })
        
        # Create test accounts
        cls.account_income = cls.env['account.account'].create({
            'name': 'Test Income Account',
            'code': '4000',
            'account_type': 'income',
            'company_id': cls.company.id,
        })
        
        cls.account_expense = cls.env['account.account'].create({
            'name': 'Test Expense Account',
            'code': '6000',
            'account_type': 'expense',
            'company_id': cls.company.id,
        })
        
        cls.account_asset = cls.env['account.account'].create({
            'name': 'Test Asset Account',
            'code': '1000',
            'account_type': 'asset_receivable',
            'company_id': cls.company.id,
        })
        
        cls.account_liability = cls.env['account.account'].create({
            'name': 'Test Liability Account',
            'code': '2000',
            'account_type': 'liability_payable',
            'company_id': cls.company.id,
        })
        
        # Create test cash forecast categories
        cls.category_income = cls.env['setu.cash.forecast.categories'].create({
            'name': 'Test Income Category',
            'type': 'income',
            'company_id': cls.company.id,
        })
        
        cls.category_expense = cls.env['setu.cash.forecast.categories'].create({
            'name': 'Test Expense Category',
            'type': 'expense',
            'company_id': cls.company.id,
        })
        
        cls.category_opening = cls.env['setu.cash.forecast.categories'].create({
            'name': 'Test Opening Category',
            'type': 'opening',
            'is_group_for_opening': True,
            'company_id': cls.company.id,
        })
        
        # Create test cash forecast types
        cls.forecast_type_income = cls.env['setu.cash.forecast.type'].create({
            'name': 'Test Income Forecast',
            'type': 'income',
            'cash_forecast_category_id': cls.category_income.id,
            'account_ids': [(6, 0, [cls.account_income.id])],
            'company_id': cls.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'calculation_pattern': 'average',
            'average_value_of_days': 30,
            'sequence': 1,
        })
        
        cls.forecast_type_expense = cls.env['setu.cash.forecast.type'].create({
            'name': 'Test Expense Forecast',
            'type': 'expense',
            'cash_forecast_category_id': cls.category_expense.id,
            'account_ids': [(6, 0, [cls.account_expense.id])],
            'company_id': cls.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'calculation_pattern': 'average',
            'average_value_of_days': 30,
            'sequence': 2,
        })
        
        cls.forecast_type_opening = cls.env['setu.cash.forecast.type'].create({
            'name': 'Test Opening Forecast',
            'type': 'opening',
            'cash_forecast_category_id': cls.category_opening.id,
            'account_ids': [(6, 0, [cls.account_asset.id])],
            'company_id': cls.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'sequence': 0,
        })
        
        cls.forecast_type_closing = cls.env['setu.cash.forecast.type'].create({
            'name': 'Test Closing Forecast',
            'type': 'closing',
            'company_id': cls.company.id,
            'auto_calculate': True,
            'sequence': 3,
        })
        
        # Create test cash forecast tag
        cls.forecast_tag = cls.env['cash.forecast.tag'].create({
            'name': 'Test Tag',
            'company_id': cls.company.id,
        })

    def create_test_move_line(self, account, amount, date_val=None, move_type='entry'):
        """Helper method to create test account move lines"""
        if date_val is None:
            date_val = date.today()
            
        move = self.env['account.move'].create({
            'move_type': move_type,
            'date': date_val,
            'company_id': self.company.id,
            'line_ids': [
                (0, 0, {
                    'account_id': account.id,
                    'debit': amount if amount > 0 else 0,
                    'credit': abs(amount) if amount < 0 else 0,
                }),
                (0, 0, {
                    'account_id': self.account_asset.id,
                    'debit': abs(amount) if amount < 0 else 0,
                    'credit': amount if amount > 0 else 0,
                }),
            ],
        })
        move.action_post()
        return move

    def create_test_cash_forecast(self, forecast_type, period, forecast_value=1000.0, real_value=0.0):
        """Helper method to create test cash forecast records"""
        return self.env['setu.cash.forecast'].create({
            'name': f'Test {forecast_type.name}',
            'forecast_type': forecast_type.type,
            'forecast_type_id': forecast_type.id,
            'forecast_period_id': period.id,
            'forecast_value': forecast_value,
            'real_value': real_value,
            'account_ids': [(6, 0, forecast_type.account_ids.ids)],
            'company_id': self.company.id,
            'forecast_date': date.today(),
        })
