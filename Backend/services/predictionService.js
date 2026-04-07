const mlClient = require("../config/mlClient");
const { env } = require("../config/env");

const RETRYABLE_STATUS_CODES = new Set([429, 502, 503, 504]);
const LOCALHOST_PATTERN = /(^https?:\/\/)?(localhost|127\.0\.0\.1)(:\d+)?/i;

function delay(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

function isRetryableError(error) {
  if (!error) return false;

  const status = error.response?.status;
  if (status && RETRYABLE_STATUS_CODES.has(status)) {
    return true;
  }

  // Covers timeouts and intermittent network failures.
  return ["ECONNABORTED", "ENOTFOUND", "ECONNREFUSED", "ECONNRESET", "EHOSTUNREACH"].includes(
    error.code
  );
}

function buildUnavailableError(lastError) {
  const likelyMisconfiguredProdUrl =
    env.NODE_ENV === "production" && LOCALHOST_PATTERN.test(env.ML_SERVICE_URL);

  const error = new Error(
    likelyMisconfiguredProdUrl
      ? "ML service URL is pointing to localhost in production. Set ML_SERVICE_URL to your deployed ML API URL."
      : "ML service is temporarily unavailable. Please retry in a few seconds."
  );
  error.statusCode = 503;
  error.details = {
    mlServiceUrl: env.ML_SERVICE_URL,
    upstreamStatus: lastError?.response?.status,
    upstreamMessage: lastError?.response?.data,
    code: lastError?.code,
  };

  return error;
}

async function requestMlService(config) {
  const attempts = Math.max(0, env.ML_RETRY_ATTEMPTS);
  let lastError;

  for (let attempt = 0; attempt <= attempts; attempt += 1) {
    try {
      return await mlClient.request(config);
    } catch (error) {
      lastError = error;
      const shouldRetry = isRetryableError(error) && attempt < attempts;

      if (!shouldRetry) {
        throw error;
      }

      await delay(env.ML_RETRY_DELAY_MS * (attempt + 1));
    }
  }

  throw buildUnavailableError(lastError);
}

async function predictDisease(symptomPayload) {
  try {
    const { data } = await requestMlService({
      method: "post",
      url: "/predict",
      data: symptomPayload,
    });
    return data;
  } catch (error) {
    if (isRetryableError(error)) {
      throw buildUnavailableError(error);
    }

    throw error;
  }
}

async function getMlHealth() {
  const { data } = await requestMlService({ method: "get", url: "/health" });
  return data;
}

module.exports = {
  predictDisease,
  getMlHealth,
};
