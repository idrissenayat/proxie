const { test, expect } = require('@playwright/test');

test.describe('Chat Page', () => {
    test('should load the chat page and show initial greeting', async ({ page }) => {
        // Navigate to the chat page
        await page.goto('/chat');

        // Check if the page title or a specific element is present
        await expect(page.locator('h2')).toContainText('Proxie AI');

        // Check for the initial assistant message
        const initialMessage = page.locator('p.leading-relaxed').first();
        await expect(initialMessage).toBeVisible();
        await expect(initialMessage).toContainText("Hi! I'm Proxie");
    });

    test('should allow typing and sending a message', async ({ page }) => {
        await page.goto('/chat');

        const input = page.locator('input[placeholder="Ask anything"]');
        const sendButton = page.locator('button:has(svg.lucide-send)');

        // Type a message
        await input.fill('I need a haircut in New York');

        // Send the message
        await sendButton.click();

        // Check if the user message appears in the chat
        await expect(page.locator('p:text("I need a haircut in New York")')).toBeVisible();

        // Check if the thinking indicator appears
        await expect(page.locator('text=Thinking...')).toBeVisible();
    });

    test('should toggle attachment menu', async ({ page }) => {
        await page.goto('/chat');

        const plusButton = page.locator('button:has(svg.lucide-plus)');
        await plusButton.click();

        // Check if attachment options are visible
        await expect(page.locator('text=Take Photo')).toBeVisible();
        await expect(page.locator('text=Choose Photo')).toBeVisible();
        await expect(page.locator('text=Choose Video')).toBeVisible();
    });
});
