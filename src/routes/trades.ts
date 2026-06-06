import { Router, Request, Response } from "express";
import { authMiddleware } from "../middleware/auth";

export const tradeRouter = Router();

// ---- 我的交换历史 ----
tradeRouter.get("/", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const trades = await prisma.tradeOffer.findMany({
    where: {
      status: "completed",
      OR: [{ proposerId: req.user!.userId }, { receiverId: req.user!.userId }],
    },
    include: {
      listing: {
        include: {
          offeredItem: { include: { definition: true } },
        },
      },
      proposer: { select: { id: true, username: true, avatarUrl: true } },
      receiver: { select: { id: true, username: true, avatarUrl: true } },
      offerItems: {
        include: { inventoryItem: { include: { definition: true } } },
      },
    },
    orderBy: { createdAt: "desc" },
  });
  res.json({ trades });
});

// ---- 交换详情 ----
tradeRouter.get("/:id", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const trade = await prisma.tradeOffer.findUnique({
    where: { id: BigInt(req.params.id) },
    include: {
      listing: {
        include: {
          offeredItem: { include: { definition: true } },
          seller: { select: { id: true, username: true } },
        },
      },
      proposer: { select: { id: true, username: true, avatarUrl: true } },
      receiver: { select: { id: true, username: true, avatarUrl: true } },
      offerItems: {
        include: { inventoryItem: { include: { definition: true } } },
      },
      eventLogs: { orderBy: { createdAt: "asc" } },
    },
  });
  if (!trade) { res.status(404).json({ error: "交换记录不存在" }); return; }
  res.json({ trade });
});
