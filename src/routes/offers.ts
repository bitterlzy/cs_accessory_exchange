import { Router, Request, Response } from "express";
import { z } from "zod";
import { authMiddleware } from "../middleware/auth";
import { validate } from "../middleware/validate";
import { AppError } from "../middleware/errorHandler";
import { getIO } from "../services/socket";

export const offerRouter = Router();

const createOfferSchema = z.object({
  listingId: z.number({ coerce: true }),
  proposerItemIds: z.array(z.number({ coerce: true })).min(1, "至少提供1件饰品"),
  note: z.string().max(500).optional(),
});

const counterOfferSchema = z.object({
  receiverItemIds: z.array(z.number({ coerce: true })).min(1, "至少提供1件饰品作为还价"),
  note: z.string().max(500).optional(),
});

// ---- 我收到/发出的提议 ----
offerRouter.get("/", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const offers = await prisma.tradeOffer.findMany({
    where: {
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
  res.json({ offers });
});

// ---- 发起提议 ----
offerRouter.post("/", authMiddleware, validate(createOfferSchema), async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const data = req.body;

  const listing = await prisma.listing.findUnique({
    where: { id: data.listingId },
    include: { seller: true },
  });
  if (!listing || listing.status !== "active") throw new AppError(404, "交换请求不存在或已关闭");
  if (listing.sellerId === req.user!.userId) throw new AppError(400, "不能对自己的请求发起交换");

  // 验证提议方物品
  const proposerItems = await prisma.inventoryItem.findMany({
    where: { id: { in: data.proposerItemIds }, ownerId: req.user!.userId, status: "available" },
  });
  if (proposerItems.length !== data.proposerItemIds.length) {
    throw new AppError(400, "部分饰品不存在或状态不可用");
  }

  // 事务创建提议
  const offer = await prisma.$transaction(async (tx) => {
    // 锁定提议方物品
    await tx.inventoryItem.updateMany({
      where: { id: { in: data.proposerItemIds } },
      data: { status: "locked" },
    });

    // 创建提议
    const offer = await tx.tradeOffer.create({
      data: {
        listingId: data.listingId,
        proposerId: req.user!.userId,
        receiverId: listing.sellerId,
        proposerNote: data.note,
        status: "pending",
        offerItems: {
          create: data.proposerItemIds.map((itemId: bigint) => ({
            inventoryItemId: itemId,
            side: "proposer",
          })),
        },
      },
      include: { offerItems: true },
    });

    // 审计日志
    await tx.eventLog.create({
      data: {
        tradeOfferId: offer.id,
        actorId: req.user!.userId,
        eventType: "offer_created",
        metadata: { listingId: data.listingId, proposerItemIds: data.proposerItemIds },
      },
    });

    // 创建通知
    await tx.notification.create({
      data: {
        userId: listing.sellerId,
        type: "new_offer",
        title: "收到新的交换提议",
        body: `${req.user!.username} 对你的「${listing.offeredItemId}」发起了交换`,
        data: { offerId: offer.id, listingId: data.listingId },
      },
    });

    return offer;
  });

  // Socket.IO 实时推送
  try {
    const io = getIO();
    io.to(`user:${listing.sellerId}`).emit("offer_update", {
      type: "new_offer",
      offerId: offer.id,
      listingId: data.listingId,
      proposerId: req.user!.userId,
      proposerName: req.user!.username,
    });
  } catch {}

  res.status(201).json({ offer });
});

// ---- 接受提议 ----
offerRouter.post("/:id/accept", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const offerId = BigInt(req.params.id);

  const offer = await prisma.tradeOffer.findUnique({
    where: { id: offerId },
  });
  if (!offer) throw new AppError(404, "提议不存在");
  if (offer.receiverId !== req.user!.userId) throw new AppError(403, "无权操作");
  if (offer.status !== "pending") throw new AppError(400, "提议状态不允许接受");

  await prisma.$transaction(async (tx) => {
    await tx.tradeOffer.update({
      where: { id: offerId },
      data: { status: "accepted", receiverNote: "已接受" },
    });
    await tx.eventLog.create({
      data: { tradeOfferId: offerId, actorId: req.user!.userId, eventType: "offer_accepted" },
    });
    await tx.notification.create({
      data: {
        userId: offer.proposerId,
        type: "offer_response",
        title: "交换提议已被接受",
        body: "对方已接受你的交换提议，请确认完成交换",
        data: { offerId },
      },
    });
  });

  try {
    const io = getIO();
    io.to(`user:${offer.proposerId}`).emit("offer_update", {
      type: "offer_accepted",
      offerId,
    });
  } catch {}

  res.json({ message: "提议已接受，请双方确认交换" });
});

// ---- 拒绝提议 ----
offerRouter.post("/:id/reject", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const offerId = BigInt(req.params.id);

  const offer = await prisma.tradeOffer.findUnique({
    where: { id: offerId },
    include: { offerItems: true },
  });
  if (!offer) throw new AppError(404, "提议不存在");
  if (offer.receiverId !== req.user!.userId) throw new AppError(403, "无权操作");
  if (offer.status !== "pending") throw new AppError(400, "提议状态不允许拒绝");

  await prisma.$transaction(async (tx) => {
    await tx.tradeOffer.update({
      where: { id: offerId },
      data: { status: "rejected" },
    });
    // 解锁物品
    for (const oi of offer.offerItems) {
      await tx.inventoryItem.update({
        where: { id: oi.inventoryItemId },
        data: { status: "available" },
      });
    }
    await tx.eventLog.create({
      data: { tradeOfferId: offerId, actorId: req.user!.userId, eventType: "offer_rejected" },
    });
  });

  try {
    const io = getIO();
    io.to(`user:${offer.proposerId}`).emit("offer_update", { type: "offer_rejected", offerId });
  } catch {}

  res.json({ message: "提议已拒绝" });
});

// ---- 确认交换 ----
offerRouter.post("/:id/confirm", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const offerId = BigInt(req.params.id);

  const offer = await prisma.tradeOffer.findUnique({
    where: { id: offerId },
    include: { offerItems: true },
  });
  if (!offer) throw new AppError(404, "提议不存在");
  if (offer.proposerId !== req.user!.userId && offer.receiverId !== req.user!.userId) {
    throw new AppError(403, "无权操作");
  }
  if (offer.status !== "accepted") throw new AppError(400, "提议尚未被接受，无法确认");

  await prisma.$transaction(async (tx) => {
    // 物品所有权转移
    const listing = await tx.listing.findUnique({
      where: { id: offer.listingId },
      include: { offeredItem: true },
    });
    if (!listing) throw new AppError(404, "关联的交换请求不存在");

    // 拿出的物品归接收方
    await tx.inventoryItem.update({
      where: { id: listing.offeredItemId },
      data: { ownerId: offer.proposerId, status: "available" },
    });

    // 提议方物品归接收方
    for (const oi of offer.offerItems) {
      await tx.inventoryItem.update({
        where: { id: oi.inventoryItemId },
        data: { ownerId: offer.receiverId, status: "available" },
      });
    }

    // 完成提议
    await tx.tradeOffer.update({
      where: { id: offerId },
      data: { status: "completed" },
    });

    // 关闭 listing
    await tx.listing.update({
      where: { id: offer.listingId },
      data: { status: "closed" },
    });

    // 更新 tracking
    await tx.listingTracking.updateMany({
      where: { listingId: offer.listingId },
      data: { status: "inactive" },
    });

    // 更新用户交换次数
    await tx.user.update({
      where: { id: offer.proposerId },
      data: { tradeCount: { increment: 1 } },
    });
    await tx.user.update({
      where: { id: offer.receiverId },
      data: { tradeCount: { increment: 1 } },
    });

    // 审计
    await tx.eventLog.create({
      data: { tradeOfferId: offerId, actorId: req.user!.userId, eventType: "trade_completed" },
    });
  });

  try {
    const io = getIO();
    io.to(`user:${offer.proposerId}`).to(`user:${offer.receiverId}`).emit("offer_update", {
      type: "trade_completed",
      offerId,
    });
  } catch {}

  res.json({ message: "交换已完成！" });
});
