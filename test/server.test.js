"use strict";
const test = require("node:test");
const assert = require("node:assert");
const app = require("../src/server");

function withServer(fn) {
  return new Promise((resolve, reject) => {
    const server = app.listen(0, async () => {
      try {
        await fn(`http://127.0.0.1:${server.address().port}`);
        resolve();
      } catch (e) {
        reject(e);
      } finally {
        server.close();
      }
    });
  });
}

test("GET /health returns ok", () =>
  withServer(async (base) => {
    const res = await fetch(`${base}/health`);
    assert.strictEqual(res.status, 200);
    assert.deepStrictEqual(await res.json(), { status: "ok" });
  }));

test("GET / reports the service name", () =>
  withServer(async (base) => {
    const body = await (await fetch(`${base}/`)).json();
    assert.strictEqual(body.service, "pipeline-security-lab");
  }));
