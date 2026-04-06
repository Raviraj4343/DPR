const express = require("express");

const { predict } = require("../controllers/predictionController");
const validateSymptoms = require("../middleware/validateSymptoms");

const router = express.Router();

router.post("/", validateSymptoms, predict);

module.exports = router;
