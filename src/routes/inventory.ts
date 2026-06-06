import { Router, Request, Response } from "express";
import { z } from "zod";
import { authMiddleware } from "../middleware/auth";
import { validate } from "../middleware/validate";
import { AppError } from "../middleware/errorHandler";

export const inventoryRouter = Router();

const createItemSchema = z.object({
  definitionId: z.number({ coerce: true }),
  quality: z.enum(["FN", "MW", "FT", "WW", "BS"]),
  floatValue: z.number().min(0).max(1).optional(),
  pattern: z.number().int().optional(),
  statTrak: z.boolean().optional().default(false),
  souvenir: z.boolean().optional().default(false),
  description: z.string().max(500).optional(),
  imageUrl: z.string().url().optional(),
});

// ---- 获取我的库存 ----
inventoryRouter.get("/", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const { status, category, quality, search } = req.query;

  const where: any = { ownerId: req.user!.userId };
  if (status) where.status = status;
  if (quality) where.quality = quality;
  if (category) {
    where.definition = { category: category as any };
  }
  if (search) {
    where.definition = {
      ...(where.definition || {}),
      name: { contains: search as string },
    };
  }

  const items = await prisma.inventoryItem.findMany({
    where,
    include: { definition: true },
    orderBy: { createdAt: "desc" },
  });

  res.json({ items });
});

// ---- 添加饰品到库存 ----
inventoryRouter.post("/", authMiddleware, validate(createItemSchema), async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const data = req.body;

  // 验证 definition 存在
  const def = await prisma.itemDefinition.findUnique({ where: { id: data.definitionId } });
  if (!def) throw new AppError(404, "装备不存在于数据字典中");

  const item = await prisma.inventoryItem.create({
    data: {
      ownerId: req.user!.userId,
      definitionId: data.definitionId,
      quality: data.quality,
      floatValue: data.floatValue,
      pattern: data.pattern,
      statTrak: data.statTrak,
      souvenir: data.souvenir,
      description: data.description,
      imageUrl: data.imageUrl,
    },
    include: { definition: true },
  });

  res.status(201).json({ item });
});

// ---- 删除库存饰品 ----
inventoryRouter.delete("/:id", authMiddleware, async (req: Request, res: Response) => {
  const { prisma } = await import("../index");
  const itemId = BigInt(req.params.id);

  const item = await prisma.inventoryItem.findUnique({ where: { id: itemId } });
  if (!item) throw new AppError(404, "饰品不存在");
  if (item.ownerId !== req.user!.userId) throw new AppError(403, "无权操作此饰品");
  if (item.status !== "available") throw new AppError(400, "饰品当前状态不允许删除");

  await prisma.inventoryItem.update({
    where: { id: itemId },
    data: { status: "removed" },
  });

  res.json({ message: "饰品已移除" });
});
