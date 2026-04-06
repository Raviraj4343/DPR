const { predictDisease } = require("../services/predictionService");

async function predict(req, res, next) {
  try {
    const result = await predictDisease(req.cleanedSymptoms);
    return res.status(200).json({
      success: true,
      data: result,
    });
  } catch (error) {
    return next(error);
  }
}

module.exports = { predict };
