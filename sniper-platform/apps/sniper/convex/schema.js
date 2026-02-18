import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  events: defineTable({
    channel: v.string(),
    event: v.string(),
    data: v.any(),
    timestamp: v.string(),
  })
    .index("by_channel", ["channel"])
    .index("by_event", ["event"])
    .index("by_timestamp", ["timestamp"]),

  snapshots: defineTable({
    key: v.string(),
    value: v.any(),
    expiresAt: v.optional(v.string()),
    updatedAt: v.string(),
  }).index("by_key", ["key"]),
});
