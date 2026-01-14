import { test, expect } from '@playwright/test';

test('analysis page is default route', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Debate & Analysis/i })).toBeVisible();
});


