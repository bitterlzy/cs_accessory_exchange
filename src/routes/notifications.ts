import { Router, Request, Response } from "express";
import { authMiddleware } from "../middleware/auth";
import { AppError } from "../middleware/errorHandler";

export const notificationRouter = Router();

// ---- 通知列表 ----
notificationRouter.get("/", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const { unreadOnly, page = "1", limit = "20" } = req.query;

  const where: any = { userId: req.user!.userId };
  if (unreadOnly === "true") where.isRead = false;

  const skip = (parseInt(page as string) - 1) * parseInt(limit as string);
  const take = parseInt(limit as string);

  const [notifications, total, unreadCount] = await Promise.all([
    prisma.notification.findMany({
      where,
      orderBy: { createdAt: "desc" },
      skip,
      take,
    }),
    prisma.notification.count({ where }),
    prisma.notification.count({ where: { userId: req.user!.userId, isRead: false } }),
  ]);

  res.json({ notifications, total, unreadCount, page: parseInt(page as string), limit: take });
});

// ---- 标记已读 ----
notificationRouter.patch("/:id/read", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const notifId = BigInt(req.params.id);

  const notif = await prisma.notification.findUnique({ where: { id: notifId } });
  if (!notif) throw new AppError(404, "通知不存在");
  if (notif.userId !== req.user!.userId) throw new AppError(403, "无权操作");

  await prisma.notification.update({
    where: { id: notifId },
    data: { isRead: true },
  });

  res.json({ message: "标记已读" });
});

// ---- 全部标记已读 ----
notificationRouter.post("/read-all", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  await prisma.notification.updateMany({
    where: { userId: req.user!.userId, isRead: false },
    data: { isRead: true },
  });
  res.json({ message: "全部标记已读" });
});
