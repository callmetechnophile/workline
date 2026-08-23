import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

/**
 * Workline AI — Next.js Edge Middleware (Clerk Authentication)
 *
 * PUBLIC ROUTES (no auth required):
 *   /              Landing page (branding only)
 *   /login         Custom Clerk login page
 *   /sign-in       Clerk sign-in catch-all
 *   /sign-up       Clerk sign-up catch-all
 *   /invite        Team invitation acceptance
 *
 * ALL OTHER ROUTES require Clerk authentication.
 * Unauthenticated requests are redirected to /sign-in.
 */
const isPublicRoute = createRouteMatcher([
  "/",
  "/login(.*)",
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/invite(.*)",
]);

export default clerkMiddleware(async (auth, request) => {
  if (!isPublicRoute(request)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
