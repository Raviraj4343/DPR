const axios = require("axios");

const { env } = require("./env");

const mlClient = axios.create({
  baseURL: env.ML_SERVICE_URL,
  timeout: env.ML_TIMEOUT_MS,
  headers: {
    "Content-Type": "application/json",
  },
});

module.exports = mlClient;
