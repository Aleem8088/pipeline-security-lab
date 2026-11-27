"use strict";
const express = require("express");

const app = express();

app.get("/", (_req, res) => {
  res.json({
    service: "pipeline-security-lab",
    version: process.env.APP_VERSION || "dev",
  });
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

if (require.main === module) {
  const port = process.env.PORT || 3000;
  app.listen(port, () => console.log(`listening on ${port}`));
}

module.exports = app;
