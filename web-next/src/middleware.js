import { clerkMiddleware } from "@clerk/nextjs/server";

export default clerkMiddleware((auth, req) => {
    // Check for E2E/Load Test bypass
    const bypassSecret = process.env.LOAD_TEST_SECRET || "proxie_load_test_key_2026";
    const headerSecret = req.headers.get("X-Load-Test-Secret");

    // Only allow bypass in non-production environments
    if (process.env.NODE_ENV !== "production") {
        if (headerSecret === bypassSecret) {
            return; // Allow bypass
        }
    }
});

export const config = {
    matcher: [
        // Skip Next.js internals and all static files, unless found in search params
        '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
        // Always run for API routes
        '/(api|trpc)(.*)',
    ],
};
