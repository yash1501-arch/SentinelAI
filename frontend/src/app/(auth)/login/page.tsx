"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Shield, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuthStore } from "@/store/auth";
import { toast } from "sonner";

const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setLoading(true);
    try {
      await login(data);
      toast.success("Welcome back!");
      router.push("/chat");
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Invalid credentials";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background to-secondary/20 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary">
            <Shield className="h-6 w-6 text-primary-foreground" />
          </div>
          <CardTitle className="text-2xl">SentinelAI</CardTitle>
          <CardDescription>
            Crime Intelligence Platform — Sign in to continue
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                placeholder="Enter your username"
                {...register("username")}
              />
              {errors.username && (
                <p className="text-xs text-destructive">
                  {errors.username.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                {...register("password")}
              />
              {errors.password && (
                <p className="text-xs text-destructive">
                  {errors.password.message}
                </p>
              )}
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </Button>
          </form>
          <p className="mt-4 text-center text-xs text-muted-foreground">
            <Link
              href="/register"
              className="text-primary hover:underline"
            >
              Create an account
            </Link>
          </p>

          {/* Demo credentials */}
          <div className="mt-4 rounded-lg border p-3">
            <p className="text-xs font-medium text-muted-foreground mb-2">
              Demo Credentials
            </p>
            <div className="grid grid-cols-3 gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="text-xs"
                onClick={() => {
                  const form = document.querySelector("form");
                  const usernameInput = form?.querySelector<HTMLInputElement>("#username");
                  const passwordInput = form?.querySelector<HTMLInputElement>("#password");
                  if (usernameInput) { usernameInput.value = "admin"; usernameInput.dispatchEvent(new Event("input", { bubbles: true })); }
                  if (passwordInput) { passwordInput.value = "Admin@123"; passwordInput.dispatchEvent(new Event("input", { bubbles: true })); }
                }}
              >
                Admin
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="text-xs"
                onClick={() => {
                  const form = document.querySelector("form");
                  const usernameInput = form?.querySelector<HTMLInputElement>("#username");
                  const passwordInput = form?.querySelector<HTMLInputElement>("#password");
                  if (usernameInput) { usernameInput.value = "investigator"; usernameInput.dispatchEvent(new Event("input", { bubbles: true })); }
                  if (passwordInput) { passwordInput.value = "Investigator@123"; passwordInput.dispatchEvent(new Event("input", { bubbles: true })); }
                }}
              >
                Investigator
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="text-xs"
                onClick={() => {
                  const form = document.querySelector("form");
                  const usernameInput = form?.querySelector<HTMLInputElement>("#username");
                  const passwordInput = form?.querySelector<HTMLInputElement>("#password");
                  if (usernameInput) { usernameInput.value = "analyst"; usernameInput.dispatchEvent(new Event("input", { bubbles: true })); }
                  if (passwordInput) { passwordInput.value = "Analyst@123"; passwordInput.dispatchEvent(new Event("input", { bubbles: true })); }
                }}
              >
                Analyst
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
