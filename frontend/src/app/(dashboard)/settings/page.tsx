"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import * as authService from "@/services/auth";
import { useAuthStore } from "@/store/auth";
import { useRouter } from "next/navigation";
import { Loader2, Save, LogOut } from "lucide-react";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const updateProfile = useAuthStore((s) => s.updateProfile);
  const logout = useAuthStore((s) => s.logout);
  const router = useRouter();

  const [fullName, setFullName] = useState(user?.full_name || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [saving, setSaving] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [changingPassword, setChangingPassword] = useState(false);

  const handleUpdateProfile = async () => {
    setSaving(true);
    try {
      await updateProfile({
        full_name: fullName,
        phone: phone || null,
      });
      toast.success("Profile updated");
    } catch {
      toast.error("Update failed");
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    setChangingPassword(true);
    try {
      await authService.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      toast.success("Password changed");
      setCurrentPassword("");
      setNewPassword("");
    } catch {
      toast.error("Failed to change password");
    } finally {
      setChangingPassword(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div className="space-y-4 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Manage your account and preferences
        </p>
      </div>

      <Tabs defaultValue="profile">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="password">Password</TabsTrigger>
          <TabsTrigger value="session">Session</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Email</Label>
                <Input value={user?.email || ""} disabled />
              </div>
              <div className="space-y-2">
                <Label>Username</Label>
                <Input value={user?.username || ""} disabled />
              </div>
              <div className="space-y-2">
                <Label>Full Name</Label>
                <Input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <Input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>
              <Button onClick={handleUpdateProfile} disabled={saving}>
                {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="password" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Change Password</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Current Password</Label>
                <Input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>New Password</Label>
                <Input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </div>
              <Button
                onClick={handleChangePassword}
                disabled={
                  changingPassword ||
                  !currentPassword ||
                  !newPassword
                }
              >
                {changingPassword && (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                )}
                Update Password
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="session" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Session</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Signed in as {user?.email} ({user?.roles?.[0]?.name})
              </p>
              <Button variant="destructive" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
