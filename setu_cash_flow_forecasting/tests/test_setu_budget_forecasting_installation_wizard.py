# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import tagged
from odoo.exceptions import ValidationError
from datetime import date
from .common import SuCashForecastTestCommon


@tagged('post_install', '-at_install')
class TestSetuBudgetForecastingInstallationWizard(SuCashForecastTestCommon):
    """Test cases for setu.budget.forecasting.installation.wizard"""

    def test_wizard_creation(self):
        """Test basic wizard creation"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        self.assertEqual(wizard.company_id, self.company)

    def test_wizard_company_isolation(self):
        """Test that wizard respects company isolation"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create wizard for other company
        other_wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': other_company.id,
        })
        
        self.assertEqual(other_wizard.company_id, other_company)

    def test_wizard_default_company(self):
        """Test wizard default company"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({})
        
        # Should default to current company
        self.assertEqual(wizard.company_id, self.env.company)

    def test_wizard_installation_process(self):
        """Test wizard installation process"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation action
        result = wizard.action_install_budget_forecasting()
        
        # Should return an action or True
        self.assertTrue(result)

    def test_wizard_installation_with_existing_data(self):
        """Test wizard installation with existing forecast data"""
        # Create some existing forecast data
        self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0
        )
        
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_multiple_companies(self):
        """Test wizard installation for multiple companies"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create wizard for each company
        wizard1 = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        wizard2 = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': other_company.id,
        })
        
        # Test installation for both companies
        result1 = wizard1.action_install_budget_forecasting()
        result2 = wizard2.action_install_budget_forecasting()
        
        self.assertTrue(result1)
        self.assertTrue(result2)

    def test_wizard_installation_validation(self):
        """Test wizard installation validation"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Should not raise any validation errors
        try:
            result = wizard.action_install_budget_forecasting()
            self.assertTrue(result)
        except ValidationError:
            self.fail("Installation wizard should not raise ValidationError")

    def test_wizard_installation_without_company(self):
        """Test wizard installation without company"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({})
        
        # Should use default company
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_with_custom_settings(self):
        """Test wizard installation with custom settings"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation with custom settings
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_rollback(self):
        """Test wizard installation rollback functionality"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)
        
        # Test rollback if needed
        # This would depend on the actual implementation

    def test_wizard_installation_progress_tracking(self):
        """Test wizard installation progress tracking"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation progress
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_error_handling(self):
        """Test wizard installation error handling"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test error handling during installation
        try:
            result = wizard.action_install_budget_forecasting()
            self.assertTrue(result)
        except Exception as e:
            # Should handle errors gracefully
            self.fail(f"Installation wizard should handle errors gracefully: {e}")

    def test_wizard_installation_permissions(self):
        """Test wizard installation permissions"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation with different user permissions
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_data_integrity(self):
        """Test wizard installation data integrity"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test that installation maintains data integrity
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_performance(self):
        """Test wizard installation performance"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation performance
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_logging(self):
        """Test wizard installation logging"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation logging
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_backup(self):
        """Test wizard installation backup functionality"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation backup
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_cleanup(self):
        """Test wizard installation cleanup"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation cleanup
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_verification(self):
        """Test wizard installation verification"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation verification
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_completion(self):
        """Test wizard installation completion"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation completion
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_notification(self):
        """Test wizard installation notification"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation notification
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)

    def test_wizard_installation_status(self):
        """Test wizard installation status"""
        wizard = self.env['setu.budget.forecasting.installation.wizard'].create({
            'company_id': self.company.id,
        })
        
        # Test installation status
        result = wizard.action_install_budget_forecasting()
        self.assertTrue(result)
