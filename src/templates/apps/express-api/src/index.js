import "dotenv/config";
import express from "express";
import cors from "cors";
import morgan from "morgan";

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(morgan("dev"));
app.use(express.json());

app.get("/", (_request, response) => {
  response.json({
    name: "express-api",
    status: "ok",
    generatedBy: "ProgressiveNodeX"
  });
});

app.get("/health", (_request, response) => {
  response.json({ ok: true });
});

app.listen(port, () => {
  console.log(`Express API running on http://localhost:${port}`);
});