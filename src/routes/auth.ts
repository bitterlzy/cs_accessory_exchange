import { Router, Request, Response } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { z } from "zod";
import { prisma } from "../index";
import { config } from "../config";
import { authMiddleware, AuthPayload } from "../middleware/auth";
import { validate } from "../middleware/validate";
import { AppError } from "../middleware/errorHandler";

export const authRouter = Router();

const registerSchema = z.object({
  email: z.string().email("邮箱格式不正确"),
  username: z.string().min(2, "用户名至少2个字符").max(50),
  password: z.string().min(6, "密码至少6个字符").max(100),
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

// ---- 注册 ----
authRouter.post("/register", validate(registerSchema), async (req: Request, res: Response) => {
  const { email, username, password } = req.body;

  const existing = await prisma.user.findFirst({
    where: { OR: [{ email }, { username }] },
  });
  if (existing) {
    throw new AppError(409, "邮箱或用户名已被注册");
  }

  const passwordHash = await bcrypt.hash(password, 12);
  const user = await prisma.user.create({
    data: { email, username, passwordHash },
  });

  const token = generateToken({ userId: user.id, username: user.username });
  const refreshToken = generateRefreshToken({ userId: user.id, username: user.username });

  res.status(201).json({
    user: { id: user.id, email: user.email, username: user.username },
    token,
    refreshToken,
  });
});

// ---- 登录 ----
authRouter.post("/login", validate(loginSchema), async (req: Request, res: Response) => {
  const { email, password } = req.body;

  const user = await prisma.user.findUnique({ where: { email } });
  if (!user || user.status === "disabled") {
    throw new AppError(401, "邮箱或密码错误");
  }

  const valid = await bcrypt.compare(password, user.passwordHash);
  if (!valid) {
    throw new AppError(401, "邮箱或密码错误");
  }

  await prisma.user.update({
    where: { id: user.id },
    data: { lastLogin: new Date() },
  });

  const token = generateToken({ userId: user.id, username: user.username });
  const refreshToken = generateRefreshToken({ userId: user.id, username: user.username });

  res.json({
    user: { id: user.id, email: user.email, username: user.username, avatarUrl: user.avatarUrl },
    token,
    refreshToken,
  });
});

// ---- 刷新令牌 ----
authRouter.post("/refresh", async (req: Request, res: Response) => {
  const { refreshToken } = req.body;
  if (!refreshToken) {
    throw new AppError(400, "缺少刷新令牌");
  }

  try {
    const decoded = jwt.verify(refreshToken, config.jwt.refreshSecret) as AuthPayload;
    const user = await prisma.user.findUnique({ where: { id: decoded.userId } });
    if (!user || user.status === "disabled") {
      throw new AppError(401, "用户不存在或已禁用");
    }

    const newToken = generateToken({ userId: user.id, username: user.username });
    const newRefreshToken = generateRefreshToken({ userId: user.id, username: user.username });

    res.json({ token: newToken, refreshToken: newRefreshToken });
  } catch {
    throw new AppError(401, "刷新令牌无效或已过期");
  }
});

// ---- 获取当前用户 ----
authRouter.get("/me", authMiddleware, async (req: Request, res: Response) => {
  const user = await prisma.user.findUnique({
    where: { id: req.user!.userId },
    select: { id: true, email: true, username: true, avatarUrl: true, steamId: true, reputationScore: true, tradeCount: true, createdAt: true },
  });
  if (!user) throw new AppError(404, "用户不存在");
  res.json({ user });
});

function generateToken(payload: AuthPayload): string {
  return jwt.sign(payload, config.jwt.secret, { expiresIn: config.jwt.expiresIn as any });
}

function generateRefreshToken(payload: AuthPayload): string {
  return jwt.sign(payload, config.jwt.refreshSecret, { expiresIn: config.jwt.refreshExpiresIn as any });
}
