import { AuthenticateWithRedirectCallback } from "@clerk/nextjs";

export default function SSOCallbackPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-200 font-mono text-xs">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
        <p>Authenticating with OAuth provider...</p>
        <AuthenticateWithRedirectCallback />
      </div>
    </div>
  );
}
