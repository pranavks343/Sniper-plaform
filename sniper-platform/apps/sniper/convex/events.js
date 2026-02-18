import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const ingestEvent = mutation({
  args: {
    channel: v.string(),
    event: v.string(),
    data: v.any(),
    timestamp: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("events", {
      channel: args.channel,
      event: args.event,
      data: args.data,
      timestamp: args.timestamp,
    });
  },
});

export const upsertSnapshot = mutation({
  args: {
    key: v.string(),
    value: v.any(),
    expiresAt: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("snapshots")
      .withIndex("by_key", (q) => q.eq("key", args.key))
      .first();

    const payload = {
      key: args.key,
      value: args.value,
      expiresAt: args.expiresAt,
      updatedAt: new Date().toISOString(),
    };

    if (existing) {
      await ctx.db.patch(existing._id, payload);
      return existing._id;
    }
    return await ctx.db.insert("snapshots", payload);
  },
});

export const latestSnapshot = query({
  args: { key: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("snapshots")
      .withIndex("by_key", (q) => q.eq("key", args.key))
      .first();
  },
});
