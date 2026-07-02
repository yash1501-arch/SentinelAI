import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const publicPaths = ["/login", "/register", "/landing"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Root path shows landing page — always public
  if (pathname === "/") {
    return NextResponse.next();
  }

  // Allow public paths and static assets
  if (publicPaths.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // All other routes handled by client-side auth in dashboard layout
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api).*)"],
};
