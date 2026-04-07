const dotenv = require("dotenv");

dotenv.config();

const env = {
  NODE_ENV: process.env.NODE_ENV || "development",
  PORT: Number(process.env.PORT || 4000),
  CORS_ORIGIN: process.env.CORS_ORIGIN || "*",
  ML_SERVICE_URL: process.env.ML_SERVICE_URL || "http://127.0.0.1:5000",
  ML_TIMEOUT_MS: Number(process.env.ML_TIMEOUT_MS || 5000),
};

const corsOrigins = String(env.CORS_ORIGIN)
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

env.CORS_ORIGINS = corsOrigins;
env.CORS_ALLOW_ALL = corsOrigins.includes("*");

module.exports = { env };
