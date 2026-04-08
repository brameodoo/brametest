# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import tagged
from odoo.exceptions import ValidationError
from datetime import date
from .common import SuCashForecastTestCommon


@tagged('post_install', '-at_install')
class TestCashForecastTag(SuCashForecastTestCommon):
    """Test cases for cash.forecast.tag model"""

    def test_cash_forecast_tag_creation(self):
        """Test basic cash forecast tag creation"""
        tag = self.env['cash.forecast.tag'].create({
            'name': 'Test Tag',
            'company_id': self.company.id,
        })
        
        self.assertEqual(tag.name, 'Test Tag')
        self.assertEqual(tag.company_id, self.company)

    def test_cash_forecast_tag_company_isolation(self):
        """Test that cash forecast tags are properly isolated by company"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create tag for other company
        other_tag = self.env['cash.forecast.tag'].create({
            'name': 'Other Company Tag',
            'company_id': other_company.id,
        })
        
        # Search for tags in original company
        company_tags = self.env['cash.forecast.tag'].search([
            ('company_id', '=', self.company.id)
        ])
        
        self.assertNotIn(other_tag, company_tags)

    def test_cash_forecast_tag_unique_constraint(self):
        """Test unique constraint on name and company"""
        # Create first tag
        self.env['cash.forecast.tag'].create({
            'name': 'Unique Tag',
            'company_id': self.company.id,
        })
        
        # Try to create duplicate - should raise ValidationError
        with self.assertRaises(ValidationError):
            self.env['cash.forecast.tag'].create({
                'name': 'Unique Tag',
                'company_id': self.company.id,
            })

    def test_cash_forecast_tag_with_forecast_types(self):
        """Test cash forecast tag with associated forecast types"""
        # Create forecast type with the tag
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Test Forecast Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'forecasting_tag': self.forecast_tag.id,
        })
        
        # Check relationship
        self.assertEqual(forecast_type.forecasting_tag, self.forecast_tag)
        
        # Search forecast types by tag
        tag_forecast_types = self.env['setu.cash.forecast.type'].search([
            ('forecasting_tag', '=', self.forecast_tag.id)
        ])
        
        self.assertIn(forecast_type, tag_forecast_types)

    def test_cash_forecast_tag_copy(self):
        """Test copying cash forecast tag"""
        original = self.forecast_tag
        copy = original.copy()
        
        self.assertNotEqual(original.id, copy.id)
        self.assertEqual(copy.name, original.name)
        self.assertEqual(copy.company_id, original.company_id)

    def test_cash_forecast_tag_name_generation(self):
        """Test cash forecast tag name generation"""
        tag = self.env['cash.forecast.tag'].create({
            'name': 'Generated Name',
            'company_id': self.company.id,
        })
        
        # Test that name is properly set
        self.assertEqual(tag.name, 'Generated Name')

    def test_cash_forecast_tag_sequence_ordering(self):
        """Test that cash forecast tags are ordered by name"""
        # Create tags in different order
        tag3 = self.env['cash.forecast.tag'].create({
            'name': 'Z Tag',
            'company_id': self.company.id,
        })
        
        tag1 = self.env['cash.forecast.tag'].create({
            'name': 'A Tag',
            'company_id': self.company.id,
        })
        
        tag2 = self.env['cash.forecast.tag'].create({
            'name': 'M Tag',
            'company_id': self.company.id,
        })
        
        tags = self.env['cash.forecast.tag'].search([
            ('company_id', '=', self.company.id)
        ])
        
        # Check ordering
        tag1_index = tags.ids.index(tag1.id)
        tag2_index = tags.ids.index(tag2.id)
        tag3_index = tags.ids.index(tag3.id)
        
        self.assertLess(tag1_index, tag2_index)
        self.assertLess(tag2_index, tag3_index)

    def test_cash_forecast_tag_with_cash_forecasts(self):
        """Test cash forecast tag with associated cash forecasts"""
        # Create forecast type with tag
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Tagged Forecast Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'forecasting_tag': self.forecast_tag.id,
        })
        
        # Create cash forecast with the tagged forecast type
        forecast = self.create_test_cash_forecast(
            forecast_type, 
            self.period_jan, 
            forecast_value=5000.0
        )
        
        # Check that forecast is associated with the tag through forecast type
        self.assertEqual(forecast.forecast_type_id.forecasting_tag, self.forecast_tag)
        
        # Search forecasts by tag
        tag_forecasts = self.env['setu.cash.forecast'].search([
            ('forecast_type_id.forecasting_tag', '=', self.forecast_tag.id)
        ])
        
        self.assertIn(forecast, tag_forecasts)

    def test_cash_forecast_tag_multiple_forecast_types(self):
        """Test cash forecast tag with multiple forecast types"""
        # Create multiple forecast types with the same tag
        forecast_type1 = self.env['setu.cash.forecast.type'].create({
            'name': 'Tagged Forecast Type 1',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'forecasting_tag': self.forecast_tag.id,
        })
        
        forecast_type2 = self.env['setu.cash.forecast.type'].create({
            'name': 'Tagged Forecast Type 2',
            'type': 'expense',
            'cash_forecast_category_id': self.category_expense.id,
            'account_ids': [(6, 0, [self.account_expense.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'forecasting_tag': self.forecast_tag.id,
        })
        
        # Check relationships
        self.assertEqual(forecast_type1.forecasting_tag, self.forecast_tag)
        self.assertEqual(forecast_type2.forecasting_tag, self.forecast_tag)
        
        # Search forecast types by tag
        tag_forecast_types = self.env['setu.cash.forecast.type'].search([
            ('forecasting_tag', '=', self.forecast_tag.id)
        ])
        
        self.assertIn(forecast_type1, tag_forecast_types)
        self.assertIn(forecast_type2, tag_forecast_types)

    def test_cash_forecast_tag_optional_relationship(self):
        """Test that cash forecast tag relationship is optional"""
        # Create forecast type without tag
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Untagged Forecast Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        # Check that tag is not set
        self.assertFalse(forecast_type.forecasting_tag)

    def test_cash_forecast_tag_color_coding(self):
        """Test cash forecast tag color coding functionality"""
        # Create tag with color
        colored_tag = self.env['cash.forecast.tag'].create({
            'name': 'Colored Tag',
            'company_id': self.company.id,
            'color': 1,  # Red color
        })
        
        self.assertEqual(colored_tag.color, 1)
        
        # Create forecast type with colored tag
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Colored Forecast Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'forecasting_tag': colored_tag.id,
        })
        
        self.assertEqual(forecast_type.forecasting_tag.color, 1)

    def test_cash_forecast_tag_description(self):
        """Test cash forecast tag with description"""
        tag = self.env['cash.forecast.tag'].create({
            'name': 'Tag with Description',
            'company_id': self.company.id,
            'description': 'This is a test tag description',
        })
        
        self.assertEqual(tag.description, 'This is a test tag description')

    def test_cash_forecast_tag_active_flag(self):
        """Test cash forecast tag active flag"""
        # Create active tag
        active_tag = self.env['cash.forecast.tag'].create({
            'name': 'Active Tag',
            'company_id': self.company.id,
            'active': True,
        })
        
        self.assertTrue(active_tag.active)
        
        # Create inactive tag
        inactive_tag = self.env['cash.forecast.tag'].create({
            'name': 'Inactive Tag',
            'company_id': self.company.id,
            'active': False,
        })
        
        self.assertFalse(inactive_tag.active)
        
        # Search for active tags only
        active_tags = self.env['cash.forecast.tag'].search([
            ('company_id', '=', self.company.id),
            ('active', '=', True)
        ])
        
        self.assertIn(active_tag, active_tags)
        self.assertNotIn(inactive_tag, active_tags)

    def test_cash_forecast_tag_archive_unarchive(self):
        """Test cash forecast tag archive and unarchive functionality"""
        tag = self.env['cash.forecast.tag'].create({
            'name': 'Archive Test Tag',
            'company_id': self.company.id,
        })
        
        # Archive the tag
        tag.active = False
        self.assertFalse(tag.active)
        
        # Unarchive the tag
        tag.active = True
        self.assertTrue(tag.active)

    def test_cash_forecast_tag_usage_count(self):
        """Test cash forecast tag usage count"""
        # Create forecast type with tag
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Usage Test Forecast Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'forecasting_tag': self.forecast_tag.id,
        })
        
        # Count usage
        usage_count = self.env['setu.cash.forecast.type'].search_count([
            ('forecasting_tag', '=', self.forecast_tag.id)
        ])
        
        self.assertEqual(usage_count, 1)
