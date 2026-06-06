import { Router, Request, Response } from "express";
import { z } from "zod";
import { authMiddleware, optionalAuth } from "../middleware/auth";
import { validate } from "../middleware/validate";
import { AppError } from "../middleware/errorHandler";

export const listingRouter = Router();

const createListingSchema = z.object({
  offeredItemId: z.number({ coerce: true }),
  wantDescription: z.string().max(1000).optional(),
  wantCategory: z.string().max(50).optional(),
  wantSpecificDefinitionId: z.number({ coerce: true }).optional(),
  wantQuality: z.string().optional().default("any"),
});

// ---- 浏览所有交换请求 ----
listingRouter.get("/", optionalAuth, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const { category, quality, search, sort, page = "1", limit = "20" } = req.query;

  const where: any = { status: "active" };
  if (category) where.wantCategory = category;
  if (quality && quality !== "any") where.wantQuality = quality;
  if (search) {
    where.OR = [
      { wantDescription: { contains: search as string } },
      { offeredItem: { definition: { name: { contains: search as string } } } },
    ];
  }

  const skip = (parseInt(page as string) - 1) * parseInt(limit as string);
  const take = parseInt(limit as string);

  const [listings, total] = await Promise.all([
    prisma.listing.findMany({
      where,
      include: {
        seller: { select: { id: true, username: true, avatarUrl: true, reputationScore: true } },
        offeredItem: { include: { definition: true } },
        wantSpecificDefinition: true,
      },
      orderBy: sort === "oldest" ? { createdAt: "asc" } : { createdAt: "desc" },
      skip,
      take,
    }),
    prisma.listing.count({ where }),
  ]);

  res.json({ listings, total, page: parseInt(page as string), limit: take });
});

// ---- 我发布的请求 ----
listingRouter.get("/my", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const listings = await prisma.listing.findMany({
    where: { sellerId: req.user!.userId },
    include: {
      offeredItem: { include: { definition: true } },
      tradeOffers: { select: { id: true, status: true, createdAt: true } },
    },
    orderBy: { createdAt: "desc" },
  });
  res.json({ listings });
});

// ---- 发布交换请求 ----
listingRouter.post("/", authMiddleware, validate(createListingSchema), async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const data = req.body;

  // 验证物品存在且属于当前用户且状态可用
  const item = await prisma.inventoryItem.findUnique({ where: { id: data.offeredItemId } });
  if (!item) throw new AppError(404, "饰品不存在");
  if (item.ownerId !== req.user!.userId) throw new AppError(403, "无权操作此饰品");
  if (item.status !== "available") throw new AppError(400, "饰品当前状态不允许上架");

  // 事务: 创建 listing + 锁定物品 + 写入 tracking
  const listing = await prisma.$transaction(async (tx) => {
    // 锁定物品
    await tx.inventoryItem.update({
      where: { id: item.id },
      data: { status: "locked" },
    });

    // 创建 listing
    const listing = await tx.listing.create({
      data: {
        sellerId: req.user!.userId,
        offeredItemId: data.offeredItemId,
        wantDescription: data.wantDescription,
        wantCategory: data.wantCategory,
        wantSpecificDefinitionId: data.wantSpecificDefinitionId,
        wantQuality: data.wantQuality || "any",
      },
    });

    // 写入上架跟踪
    await tx.listingTracking.create({
      data: {
        definitionId: item.definitionId,
        userId: req.user!.userId,
        listingId: listing.id,
      },
    });

    return listing;
  });

  const result = await prisma.listing.findUnique({
    where: { id: listing.id },
    include: {
      seller: { select: { id: true, username: true, avatarUrl: true } },
      offeredItem: { include: { definition: true } },
    },
  });

  res.status(201).json({ listing: result });
});

// ---- 关闭交换请求 ----
listingRouter.patch("/:id/close", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const listingId = BigInt(req.params.id);

  const listing = await prisma.listing.findUnique({
    where: { id: listingId },
    include: { offeredItem: true },
  });
  if (!listing) throw new AppError(404, "交换请求不存在");
  if (listing.sellerId !== req.user!.userId) throw new AppError(403, "无权操作");

  await prisma.$transaction(async (tx) => {
    await tx.listing.update({
      where: { id: listingId },
      data: { status: "cancelled" },
    });
    await tx.listingTracking.updateMany({
      where: { listingId },
      data: { status: "inactive" },
    });
    // 解锁物品
    await tx.inventoryItem.update({
      where: { id: listing.offeredItemId },
      data: { status: "available" },
    });
  });

  res.json({ message: "交换请求已关闭" });
});
