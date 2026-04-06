const express = require("express");

const healthRoutes = require("./healthRoutes");
const predictionRoutes = require("./predictionRoutes");

const router = express.Router();

router.use("/health", healthRoutes);
router.use("/predict", predictionRoutes);

module.exports = router;
