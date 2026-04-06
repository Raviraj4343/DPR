const mlClient = require("../config/mlClient");

async function predictDisease(symptomPayload) {
  const { data } = await mlClient.post("/predict", symptomPayload);
  return data;
}

async function getMlHealth() {
  const { data } = await mlClient.get("/health");
  return data;
}

module.exports = {
  predictDisease,
  getMlHealth,
};
