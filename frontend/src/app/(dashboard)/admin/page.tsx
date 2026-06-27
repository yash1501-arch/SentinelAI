"use client";

import { useState, useEffect } from "react";
import * as adminService from "@/services/admin";
import type { User, AuditLog } from "@/types";
import { toast } from "sonner";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, UserX, UserCheck } from "lucide-react";

export default function AdminPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [formData, setFormData] = useState({
    email: "", username: "", full_name: "", password: "",
    role: "investigator", department: "", designation: "",
  });

  const loadData = () => {
    setLoading(true);
    Promise.all([
      adminService.getUsers().then(setUsers),
      adminService.getAuditLogs().then(setLogs),
    ]).finally(() => setLoading(false));
  };

  useEffect(() => { loadData(); }, []);

  const handleCreate = async () => {
    try {
      await adminService.createUser(formData);
      toast.success("User created successfully");
      setCreateOpen(false);
      setFormData({ email: "", username: "", full_name: "", password: "", role: "investigator", department: "", designation: "" });
      loadData();
    } catch {
      toast.error("Failed to create user");
    }
  };

  const handleToggleActive = async (userId: string, currentActive: boolean) => {
    try {
      await adminService.deactivateUser(userId);
      toast.success(currentActive ? "User deactivated" : "User activated");
      loadData();
    } catch {
      toast.error("Action failed");
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Admin Panel</h1>
          <p className="text-sm text-muted-foreground">User management and system audit</p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4 mr-2" /> Create User
        </Button>
      </div>

      <Tabs defaultValue="users">
        <TabsList>
          <TabsTrigger value="users">Users ({users.length})</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs ({logs.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="mt-4">
          <Card>
            <CardContent className="p-0">
              {loading ? (
                <div className="space-y-3 p-4">
                  {Array.from({ length: 3 }).map((_, i) => (<Skeleton key={i} className="h-12 w-full" />))}
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Username</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((u) => (
                      <TableRow key={u.id}>
                        <TableCell className="font-medium">{u.full_name}</TableCell>
                        <TableCell>{u.email}</TableCell>
                        <TableCell>{u.username}</TableCell>
                        <TableCell><Badge variant="outline">{u.roles?.[0]?.name || "user"}</Badge></TableCell>
                        <TableCell>
                          <Badge variant={u.is_active ? "default" : "secondary"}>
                            {u.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost" size="sm"
                            onClick={() => handleToggleActive(u.id, u.is_active)}
                          >
                            {u.is_active ? <UserX className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit" className="mt-4">
          <Card>
            <CardContent className="p-0">
              {loading ? (
                <div className="space-y-3 p-4">
                  {Array.from({ length: 3 }).map((_, i) => (<Skeleton key={i} className="h-12 w-full" />))}
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Action</TableHead>
                      <TableHead>Resource</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Date</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {logs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell><Badge variant="outline" className="text-xs">{log.action}</Badge></TableCell>
                        <TableCell className="text-sm">{log.resource_type}</TableCell>
                        <TableCell className="text-sm text-muted-foreground">{log.description || "-"}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">{new Date(log.created_at).toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create User Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Create New User</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>Full Name</Label>
                <Input value={formData.full_name} onChange={(e) => setFormData(f => ({...f, full_name: e.target.value}))} />
              </div>
              <div className="space-y-1">
                <Label>Username</Label>
                <Input value={formData.username} onChange={(e) => setFormData(f => ({...f, username: e.target.value}))} />
              </div>
            </div>
            <div className="space-y-1">
              <Label>Email</Label>
              <Input type="email" value={formData.email} onChange={(e) => setFormData(f => ({...f, email: e.target.value}))} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>Password</Label>
                <Input type="password" value={formData.password} onChange={(e) => setFormData(f => ({...f, password: e.target.value}))} />
              </div>
              <div className="space-y-1">
                <Label>Role</Label>
                <Select value={formData.role} onValueChange={(v) => setFormData(f => ({...f, role: v || "investigator"}))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="supervisor">Supervisor</SelectItem>
                    <SelectItem value="investigator">Investigator</SelectItem>
                    <SelectItem value="analyst">Analyst</SelectItem>
                    <SelectItem value="policymaker">Policymaker</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>Department</Label>
                <Input value={formData.department} onChange={(e) => setFormData(f => ({...f, department: e.target.value}))} />
              </div>
              <div className="space-y-1">
                <Label>Designation</Label>
                <Input value={formData.designation} onChange={(e) => setFormData(f => ({...f, designation: e.target.value}))} />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancel</Button>
            <Button onClick={handleCreate}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
