import cloudflare from "@astrojs/cloudflare";
import node from "@astrojs/node";
import react from "@astrojs/react";
import tailwind from "@astrojs/tailwind";
import { defineConfig } from "astro/config";

const adapterTarget = process.env.ASTRO_ADAPTER === "node" ? "node" : "cloudflare";

export default defineConfig({
  output: "server",
  adapter: adapterTarget === "node" ? node({ mode: "standalone" }) : cloudflare(),
  integrations: [react(), tailwind({ applyBaseStyles: false })],
});
