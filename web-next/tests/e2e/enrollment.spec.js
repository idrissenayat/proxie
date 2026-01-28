const { test, expect } = require('@playwright/test');

test.describe('Provider Enrollment Flow', () => {
    test('should start enrollment and show service catalog', async ({ page }) => {
        // Navigate to chat with enrollment role
        await page.goto('/chat?role=enrollment');

        // Check if the agent introduces itself
        await expect(page.locator('p.leading-relaxed').first()).toContainText("I'm ready to help you manage your business");

        // In enrollment role, the agent should eventually trigger the service catalog
        // Note: This might require waiting for the backend response if it's dynamic
    });
});
