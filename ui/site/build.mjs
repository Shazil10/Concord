import { build } from "esbuild";
import { mkdir, writeFile } from "node:fs/promises";

await mkdir("dist", { recursive: true });

await build({
  stdin: {
    contents: `
      import { createRoot } from "react-dom/client";
      import Concord from "./App.tsx";
      createRoot(document.getElementById("root")).render(<Concord />);
    `,
    loader: "tsx",
    resolveDir: ".",
  },
  bundle: true,
  minify: true,
  jsx: "automatic",
  define: { "process.env.NODE_ENV": '"production"' },
  outfile: "dist/app.js",
});

await writeFile(
  "dist/index.html",
  `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Concord · pre-settlement checks</title>
    <meta name="description" content="An AI agent that cross-checks every trade before payments are released." />
    <style>body{margin:0}</style>
  </head>
  <body>
    <div id="root"></div>
    <script src="/app.js"></script>
  </body>
</html>
`,
);
