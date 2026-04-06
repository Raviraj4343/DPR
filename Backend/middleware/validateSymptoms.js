const { symptomFields } = require("../models/symptomInput.model");

function toBinary(value, field) {
  if (value === undefined || value === null || value === "") return 0;

  if (typeof value === "boolean") return value ? 1 : 0;

  if (typeof value === "number") {
    if (value === 0 || value === 1) return value;
    throw new Error(`Invalid numeric value for ${field}. Use 0 or 1.`);
  }

  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (["1", "true", "yes", "y", "on"].includes(normalized)) return 1;
    if (["0", "false", "no", "n", "off"].includes(normalized)) return 0;
  }

  throw new Error(`Invalid value for ${field}. Use boolean, 0/1, or yes/no.`);
}

function validateSymptoms(req, res, next) {
  const payload = req.body;

  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return res.status(400).json({
      success: false,
      message: "Request body must be a JSON object.",
    });
  }

  const cleaned = {};
  try {
    for (const field of symptomFields) {
      cleaned[field] = toBinary(payload[field], field);
    }
  } catch (error) {
    return res.status(400).json({
      success: false,
      message: error.message,
    });
  }

  req.cleanedSymptoms = cleaned;
  return next();
}

module.exports = validateSymptoms;
