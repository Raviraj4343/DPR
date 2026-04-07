const express = require("express");
const cors = require("cors");
const helmet = require("helmet");
const morgan = require("morgan");

const { env } = require("./config/env");
const apiRoutes = require("./routes");
const notFound = require("./middleware/notFound");
const errorHandler = require("./middleware/errorHandler");

const app = express();

const allowedOrigins = new Set(env.CORS_ORIGINS || []);

const corsOptions = {
	origin(origin, callback) {
		if (!origin || env.CORS_ALLOW_ALL || allowedOrigins.has(origin)) {
			return callback(null, true);
		}

		return callback(new Error("Not allowed by CORS"));
	},
};

app.use(helmet());
app.use(cors(corsOptions));
app.use(express.json({ limit: "1mb" }));
app.use(morgan("dev"));

app.use("/api/v1", apiRoutes);

app.use(notFound);
app.use(errorHandler);

app.listen(env.PORT, () => {
	console.log(`Backend running on http://localhost:${env.PORT}`);
	console.log(`ML service target: ${env.ML_SERVICE_URL}`);
});

