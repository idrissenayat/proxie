const { test, expect } = require('@playwright/test');

test.describe('End-to-End User Journeys', () => {

    test('Consumer: Complete Service Request Flow', async ({ page }) => {
        // 1. Landing & Initial Chat
        await page.goto('/chat');
        await expect(page.locator('h2')).toContainText('Proxie AI');

        // 2. Describe Need
        const input = page.locator('input[placeholder="Ask anything"]');
        await input.fill('I need a professional cleaning service for my 2-bedroom apartment in Brooklyn');
        await page.keyboard.press('Enter');

        // 3. Wait for AI Interpretation (Thinking -> Response)
        await expect(page.locator('text=Thinking...')).toBeVisible();
        // We expect the agent to eventually show a draft or ask questions
        // Since we are hitting a real/mocked backend, we look for the draft card
        await expect(page.locator('text=Confirm Request')).toBeVisible({ timeout: 15000 });

        // 4. Review & Approve Draft
        // Look for the "Approve" button
        const approveButton = page.locator('button:has-text("Post Request")');
        if (await approveButton.isVisible()) {
            await approveButton.click();
        } else {
            // Fallback to typing "Post Request"
            await input.fill('Post Request');
            await page.keyboard.press('Enter');
        }

        // 5. Success Confirmation
        // 5. Success Confirmation
        await expect(page.locator('text=Your request has been posted')).toBeVisible({ timeout: 10000 });
    });

    test('Provider: Lead Management Flow', async ({ page }) => {
        // Navigate with provider role
        await page.goto('/chat?role=provider');

        // Check if provider view loads
        await expect(page.locator('text=manage active offers')).toBeVisible();

        // Request leads
        const input = page.locator('input[placeholder="Ask anything"]');
        await input.fill('Show me my new leads');
        await page.keyboard.press('Enter');

        // Wait for leads list
        await expect(page.locator('text=Thinking...')).toBeVisible();

        // In our implementation, tool results should be processed.
        // Let's look for a specific lead indicator or the mock response text
        await expect(page.locator('text=current leads')).toBeVisible({ timeout: 15000 });
    });

    test('Enrollment: Multi-step Onboarding', async ({ page }) => {
        await page.goto('/chat?role=enrollment');

        // 1. Greeting
        await expect(page.locator('p.leading-relaxed').first()).toContainText("enroll as a provider");

        // 2. Provide Name
        const input = page.locator('input[placeholder="Ask anything"]');
        await input.fill('My name is Alex and I am a pro cleaner');
        await page.keyboard.press('Enter');

        // 3. Wait for Service Catalog trigger
        // We implemented UI Hints for "service_selector"
        await expect(page.locator('text=What do you offer?')).toBeVisible({ timeout: 15000 });
    });

});
