import { Server as SocketIOServer, Socket } from "socket.io";
import jwt from "jsonwebtoken";
import { config } from "../config";

let io: SocketIOServer | null = null;

export const getIO = (): SocketIOServer => {
  if (!io) throw new Error("Socket.IO not initialized");
  return io;
};

export const setupSocketHandlers = (serverIO: SocketIOServer): void => {
  io = serverIO;

  io.use((socket: Socket, next) => {
    const token = socket.handshake.query.token as string;
    if (!token) {
      next(new Error("Authentication required"));
      return;
    }

    try {
      const decoded = jwt.verify(token, config.jwt.secret) as any;
      (socket as any).userId = decoded.userId;
      (socket as any).username = decoded.username;
      next();
    } catch {
      next(new Error("Invalid token"));
    }
  });

  io.on("connection", (socket: Socket) => {
    const userId = (socket as any).userId;
    const username = (socket as any).username;

    console.log(`[WS] User connected: ${username} (${userId})`);

    // 加入个人房间
    socket.join(`user:${userId}`);

    // 广播在线状态
    io.emit("user_online", { userId, username, online: true });

    // 处理断开
    socket.on("disconnect", () => {
      console.log(`[WS] User disconnected: ${username} (${userId})`);
      io?.emit("user_online", { userId, username, online: false });
    });

    // 处理错误
    socket.on("error", (err) => {
      console.error(`[WS] Socket error for user ${userId}:`, err.message);
    });
  });
};
