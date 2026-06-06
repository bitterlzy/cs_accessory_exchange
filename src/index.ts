import express from "express";
import cors from "cors";
import http from "http";
import { Server as SocketIOServer } from "socket.io";
import { PrismaClient } from "@prisma/client";
import { config } from "./config";
import { errorHandler } from "./middleware/errorHandler";
import { authRouter } from "./routes/auth";
import { userRouter } from "./routes/users";
import { inventoryRouter } from "./routes/inventory";
import { listingRouter } from "./routes/listings";
import { offerRouter } from "./routes/offers";
import { tradeRouter } from "./routes/trades";
import { notificationRouter } from "./routes/notifications";
import { setupSocketHandlers } from "./services/socket";

export const prisma = new PrismaClient();

const app = express();
const server = http.createServer(app);
const io = new SocketIOServer(server, {
  cors: { origin: config.cors.origin, credentials: true },
  pingInterval: 25000,
  pingTimeout: 20000,
});

// ---- Middleware ----
app.use(cors({ origin: config.cors.origin, credentials: true }));
app.use(express.json({ limit: "1mb" }));

// ---- Health Check ----
app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// ---- Routes ----
app.use("/api/auth", authRouter);
app.use("/api/users", userRouter);
app.use("/api/inventory", inventoryRouter);
app.use("/api/listings", listingRouter);
app.use("/api/offers", offerRouter);
app.use("/api/trades", tradeRouter);
app.use("/api/notifications", notificationRouter);

// ---- Error Handler (must be last) ----
app.use(errorHandler);

// ---- Socket.IO ----
setupSocketHandlers(io);

// ---- Start ----
server.listen(config.port, () => {
  console.log(`[CS-Trade] Server running on port ${config.port}`);
  console.log(`[CS-Trade] Environment: ${config.env}`);
});

// ---- Graceful Shutdown ----
const shutdown = async () => {
  console.log("[CS-Trade] Shutting down gracefully...");
  io.close();
  await prisma.$disconnect();
  server.close(() => process.exit(0));
};

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

export { app, server, io };
