const { getMlHealth } = require("../services/predictionService");

async function healthCheck(req, res, next) {
  try {
    const ml = await getMlHealth();
    return res.status(200).json({
      status: "ok",
      backend: "running",
      mlService: ml,
    });
  } catch (error) {
    return next(error);
  }
}

module.exports = { healthCheck };
