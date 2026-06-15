export function ErrorPage() {
  return (
    <div className="flex flex-col items-center justify-center h-screen space-y-4 bg-gray-50 p-6">
      <h1 className="text-2xl font-bold">Something went wrong</h1>
      <p className="text-muted-foreground text-center">Please try refreshing the page. If the problem persists, contact your administrator.</p>
      <button
        className="mt-2 text-sm underline text-muted-foreground hover:text-foreground"
        onClick={() => window.location.reload()}
      >
        Refresh
      </button>
    </div>
  );
}
