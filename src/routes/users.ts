import { Router, Request, Response } from "express";
import { authMiddleware } from "../middleware/auth";

export const userRouter = Router();

userRouter.get("/", (_req: Request, res: Response) => {
  res.json({ message: "用户管理模块" });
});

userRouter.get("/me", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const user = await prisma.user.findUnique({
    where: { id: req.user!.userId },
    select: {
      id: true, email: true, username: true, avatarUrl: true,
      steamId: true, reputationScore: true, tradeCount: true,
      createdAt: true,
    },
  });
  if (!user) { res.status(404).json({ error: "用户不存在" }); return; }
  res.json({ user });
});

userRouter.get("/:id", async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const user = await prisma.user.findUnique({
    where: { id: BigInt(req.params.id) },
    select: {
      id: true, username: true, avatarUrl: true,
      reputationScore: true, tradeCount: true, createdAt: true,
    },
  });
  if (!user) { res.status(404).json({ error: "用户不存在" }); return; }
  res.json({ user });
});
