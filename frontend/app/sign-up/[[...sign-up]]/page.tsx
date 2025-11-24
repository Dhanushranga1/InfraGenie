import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      <SignUp
        appearance={{
          elements: {
            rootBox: "mx-auto",
            card: "bg-zinc-900 border border-zinc-800 shadow-2xl",
            headerTitle: "text-white",
            headerSubtitle: "text-zinc-400",
            socialButtonsBlockButton: "bg-zinc-800 border-zinc-700 hover:bg-zinc-700 text-white",
            formButtonPrimary: "bg-violet-600 hover:bg-violet-700",
            footerActionLink: "text-violet-500 hover:text-violet-400",
            formFieldInput: "bg-zinc-800 border-zinc-700 text-white",
            formFieldLabel: "text-zinc-300",
            dividerLine: "bg-zinc-700",
            dividerText: "text-zinc-500",
          },
        }}
      />
    </div>
  );
}
