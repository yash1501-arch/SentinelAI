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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import * as authService from "@/services/auth";
import { toast } from "sonner";

const registerSchema = z
  .object({
    email: z.string().email("Valid email required"),
    username: z.string().min(3, "Username must be at least 3 characters"),
    full_name: z.string().min(1, "Full name required"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirm_password: z.string(),
    phone: z.string().optional(),
    designation: z.string().optional(),
    badge_number: z.string().optional(),
    department: z.string().optional(),
    jurisdiction: z.string().optional(),
    preferred_language: z.string().optional(),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: { preferred_language: "en" },
  });

  const onSubmit = async (data: RegisterForm) => {
    setLoading(true);
    try {
      const payload = { ...data };
      delete (payload as Record<string, unknown>).confirm_password;
      await authService.register(payload);
      toast.success("Account created! Please sign in.");
      router.push("/login");
    } catch {
      toast.error("Registration failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background to-secondary/20 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary">
            <Shield className="h-6 w-6 text-primary-foreground" />
          </div>
          <CardTitle className="text-2xl">Create Account</CardTitle>
          <CardDescription>Register for SentinelAI</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input id="full_name" {...register("full_name")} />
                {errors.full_name && (
                  <p className="text-xs text-destructive">
                    {errors.full_name.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input id="username" {...register("username")} />
                {errors.username && (
                  <p className="text-xs text-destructive">
                    {errors.username.message}
                  </p>
                )}
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" {...register("email")} />
              {errors.email && (
                <p className="text-xs text-destructive">
                  {errors.email.message}
                </p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  {...register("password")}
                />
                {errors.password && (
                  <p className="text-xs text-destructive">
                    {errors.password.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm_password">Confirm</Label>
                <Input
                  id="confirm_password"
                  type="password"
                  {...register("confirm_password")}
                />
                {errors.confirm_password && (
                  <p className="text-xs text-destructive">
                    {errors.confirm_password.message}
                  </p>
                )}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input id="phone" {...register("phone")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="designation">Designation</Label>
                <Input id="designation" {...register("designation")} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="badge_number">Badge Number</Label>
                <Input id="badge_number" {...register("badge_number")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="department">Department</Label>
                <Input id="department" {...register("department")} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="jurisdiction">Jurisdiction</Label>
                <Input id="jurisdiction" {...register("jurisdiction")} />
              </div>
              <div className="space-y-2">
                <Label>Language</Label>
                <Select
                  defaultValue="en"
                  onValueChange={(v) =>
                    setValue("preferred_language", v || "en")
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="kn">ಕನ್ನಡ (Kannada)</SelectItem>
                    <SelectItem value="hi">हिन्दी (Hindi)</SelectItem>
                    <SelectItem value="ta">தமிழ் (Tamil)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create Account"
              )}
            </Button>
          </form>
          <p className="mt-4 text-center text-xs text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
